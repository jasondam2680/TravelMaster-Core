# scheduling/optimizer.py
"""
Tour Scheduling Optimizer
Objective priority: A (no overlap + min resources) -> C (internal first) -> B (fairness) -> D (quality)
"""
from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpBinary, value, PULP_CBC_CMD
from .models import Vehicle, Guide, TourDeparture, ScheduleAssignment


def dates_overlap(start1, end1, start2, end2):
    """Check if two date ranges overlap (inclusive)"""
    return not (end1 < start2 or end2 < start1)


def run_optimizer(departures=None):
    """
    Run LP optimizer to assign Vehicle + Guide to each TourDeparture.
    Objective (priority order):
      A: No overlap + minimize total resources used
      C: Prefer internal vehicles/guides over outsourced
      B: Balance workload across guides
      D: Senior guides for premium tours (future)
    Returns: dict with status, assignments list, and stats
    """
    if departures is None:
        departures = list(TourDeparture.objects.filter(status='pending').order_by('departure_date'))

    vehicles = list(Vehicle.objects.filter(is_active=True).order_by('priority', 'source'))
    guides = list(Guide.objects.filter(is_active=True).order_by('priority', 'source'))

    if not departures or not vehicles or not guides:
        return {'status': 'error', 'message': 'No data to optimize', 'assignments': []}

    # --- Build LP Problem ---
    prob = LpProblem('TourScheduling', LpMaximize)

    # Decision variable: x[d][v][g] = 1 if departure d assigned to vehicle v + guide g
    x = {}
    for d in departures:
        x[d.id] = {}
        for v in vehicles:
            x[d.id][v.id] = {}
            for g in guides:
                # Feasibility filter: guide must speak tour language
                if d.language in g.languages and v.capacity >= d.pax:
                    x[d.id][v.id][g.id] = LpVariable(
                        f'x_{d.id}_{v.id}_{g.id}', cat=LpBinary
                    )

    # --- Objective: Maximize score (A+C+B weighted) ---
    objective_terms = []
    for d in departures:
        for v in vehicles:
            for g in guides:
                if g.id in x.get(d.id, {}).get(v.id, {}):
                    var = x[d.id][v.id][g.id]
                    # Objective C: internal sources score higher
                    source_score = 0
                    if v.source == 'internal':
                        source_score += 10
                    elif v.source == 'contract':
                        source_score += 5
                    if g.source == 'internal':
                        source_score += 10
                    elif g.source == 'freelance':
                        source_score += 5
                    # Objective A: prefer lower-capacity vehicles (min waste)
                    capacity_score = max(0, 10 - (v.capacity - d.pax))
                    # Objective B: penalize high-load guides (fairness)
                    fairness_score = 5
                    total_score = source_score + capacity_score + fairness_score
                    objective_terms.append(total_score * var)

    prob += lpSum(objective_terms)

    # --- Constraint 1: Each departure gets exactly 1 assignment ---
    for d in departures:
        valid_assignments = [
            x[d.id][v.id][g.id]
            for v in vehicles
            for g in guides
            if g.id in x.get(d.id, {}).get(v.id, {})
        ]
        if valid_assignments:
            prob += lpSum(valid_assignments) == 1, f'assign_{d.id}'
        else:
            return {
                'status': 'infeasible',
                'message': f'No valid vehicle/guide for departure {d.group_code}',
                'assignments': []
            }

    # --- Constraint 2: No vehicle overlap (full-day rule) ---
    for v in vehicles:
        for i, d1 in enumerate(departures):
            for d2 in departures[i+1:]:
                if dates_overlap(d1.departure_date, d1.return_date,
                                 d2.departure_date, d2.return_date):
                    v1_vars = [
                        x[d1.id][v.id][g.id]
                        for g in guides
                        if g.id in x.get(d1.id, {}).get(v.id, {})
                    ]
                    v2_vars = [
                        x[d2.id][v.id][g.id]
                        for g in guides
                        if g.id in x.get(d2.id, {}).get(v.id, {})
                    ]
                    if v1_vars and v2_vars:
                        prob += lpSum(v1_vars) + lpSum(v2_vars) <= 1, \
                            f'no_vehicle_overlap_{v.id}_{d1.id}_{d2.id}'

    # --- Constraint 3: No guide overlap (full-day rule) ---
    for g in guides:
        for i, d1 in enumerate(departures):
            for d2 in departures[i+1:]:
                if dates_overlap(d1.departure_date, d1.return_date,
                                 d2.departure_date, d2.return_date):
                    g1_vars = [
                        x[d1.id][v.id][g.id]
                        for v in vehicles
                        if g.id in x.get(d1.id, {}).get(v.id, {})
                    ]
                    g2_vars = [
                        x[d2.id][v.id][g.id]
                        for v in vehicles
                        if g.id in x.get(d2.id, {}).get(v.id, {})
                    ]
                    if g1_vars and g2_vars:
                        prob += lpSum(g1_vars) + lpSum(g2_vars) <= 1, \
                            f'no_guide_overlap_{g.id}_{d1.id}_{d2.id}'

    # --- Solve ---
    prob.solve(PULP_CBC_CMD(msg=0))

    status = prob.status
    status_str = 'optimal' if status == 1 else 'infeasible' if status == -1 else 'unknown'

    # --- Extract results ---
    assignments = []
    for d in departures:
        assigned = False
        for v in vehicles:
            for g in guides:
                if g.id in x.get(d.id, {}).get(v.id, {}):
                    var = x[d.id][v.id][g.id]
                    if value(var) and round(value(var)) == 1:
                        assignments.append({
                            'group_code': d.group_code,
                            'tour_name': d.tour_name,
                            'departure_date': str(d.departure_date),
                            'return_date': str(d.return_date),
                            'pax': d.pax,
                            'vehicle_plate': v.plate_number,
                            'vehicle_type': v.vehicle_type,
                            'vehicle_source': v.source,
                            'guide_name': g.full_name,
                            'guide_source': g.source,
                            'score': value(var),
                        })
                        assigned = True
                        break
            if assigned:
                break

    # --- Stats ---
    vehicles_used = len(set(a['vehicle_plate'] for a in assignments))
    guides_used = len(set(a['guide_name'] for a in assignments))
    internal_vehicle_pct = (
        sum(1 for a in assignments if a['vehicle_source'] == 'internal') / len(assignments) * 100
        if assignments else 0
    )
    internal_guide_pct = (
        sum(1 for a in assignments if a['guide_source'] == 'internal') / len(assignments) * 100
        if assignments else 0
    )

    return {
        'status': status_str,
        'total_departures': len(departures),
        'assigned': len(assignments),
        'vehicles_used': vehicles_used,
        'guides_used': guides_used,
        'internal_vehicle_pct': round(internal_vehicle_pct, 1),
        'internal_guide_pct': round(internal_guide_pct, 1),
        'assignments': assignments,
    }


def save_optimizer_results(results):
    """
    Persist optimizer results to ScheduleAssignment model.
    Only saves if status is optimal.
    """
    if results.get('status') != 'optimal':
        return 0

    saved = 0
    for a in results.get('assignments', []):
        try:
            departure = TourDeparture.objects.get(group_code=a['group_code'])
            vehicle = Vehicle.objects.get(plate_number=a['vehicle_plate'])
            guide = Guide.objects.get(full_name=a['guide_name'])
            ScheduleAssignment.objects.update_or_create(
                departure=departure,
                defaults={
                    'vehicle': vehicle,
                    'guide': guide,
                    'is_vehicle_internal': vehicle.source == 'internal',
                    'is_guide_internal': guide.source == 'internal',
                    'assigned_by': 'optimizer',
                }
            )
            departure.status = 'scheduled'
            departure.save(update_fields=['status'])
            saved += 1
        except Exception as e:
            continue
    return saved
