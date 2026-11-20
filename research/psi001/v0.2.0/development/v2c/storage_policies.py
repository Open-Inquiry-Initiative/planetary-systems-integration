"""Finite-menu scheduling controls for an unidentifiable coordination contrast."""
from dataclasses import dataclass
import math

from storage_dispatch import Dispatch, HourResult, evaluate_schedule


COORDINATION_IDENTIFIABLE = False


@dataclass(frozen=True)
class Selection:
    candidate_index: int
    schedule: tuple[Dispatch, ...]
    hourly: tuple[HourResult, ...]
    unmet_electricity: float
    unmet_heat: float
    dispatch_cost: float


def select_schedule(plant, hours, candidates, *, initial_soc, terminal_soc):
    """Choose the best feasible schedule in the ordered, shared finite menu."""
    hours = tuple(hours)
    best = None
    best_rank = None
    last_rejection = None
    for index, candidate in enumerate(candidates):
        schedule = tuple(candidate)
        try:
            hourly = evaluate_schedule(plant, hours, schedule,
                                       initial_soc=initial_soc, terminal_soc=terminal_soc)
        except ValueError as error:
            last_rejection = error
            continue
        unmet_electricity = math.fsum(row.unmet_electricity for row in hourly)
        unmet_heat = math.fsum(row.unmet_heat for row in hourly)
        dispatch_cost = math.fsum(row.realized_cost for row in hourly)
        rank = (unmet_electricity, unmet_heat, dispatch_cost, index)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best = Selection(index, schedule, hourly, unmet_electricity, unmet_heat, dispatch_cost)
    if best is None:
        raise ValueError("no feasible candidate schedule") from last_rejection
    return best


@dataclass(frozen=True)
class Controls:
    independent: Selection
    coordinated_control: Selection
    coordination_identifiable: bool = COORDINATION_IDENTIFIABLE


def compare_controls(plant, hours, candidates, *, initial_soc, terminal_soc):
    """Apply the identical scheduling policy and decision rights to both labels."""
    selection = select_schedule(plant, hours, candidates,
                                initial_soc=initial_soc, terminal_soc=terminal_soc)
    return Controls(selection, selection)
