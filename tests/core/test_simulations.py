from policyengine_core.country_template.situation_examples import single
from policyengine_core.simulations import SimulationBuilder
from policyengine_core.simulations.sim_macro_cache import SimulationMacroCache
import importlib.metadata
import numpy as np


def test_calculate_full_tracer(tax_benefit_system):
    simulation = SimulationBuilder().build_default_simulation(
        tax_benefit_system
    )
    simulation.trace = True
    simulation.calculate("income_tax", "2017-01")

    income_tax_node = simulation.tracer.trees[0]
    assert income_tax_node.name == "income_tax"
    assert str(income_tax_node.period) == "2017-01"
    assert income_tax_node.value == 0

    salary_node = income_tax_node.children[0]
    assert salary_node.name == "salary"
    assert str(salary_node.period) == "2017-01"


def test_get_entity_not_found(tax_benefit_system):
    simulation = SimulationBuilder().build_default_simulation(
        tax_benefit_system
    )
    assert simulation.get_entity(plural="no_such_entities") is None


def test_clone(tax_benefit_system):
    simulation = SimulationBuilder().build_from_entities(
        tax_benefit_system,
        {
            "persons": {
                "bill": {"salary": {"2017-01": 3000}},
            },
            "households": {"household": {"parents": ["bill"]}},
        },
    )

    simulation_clone = simulation.clone()
    assert simulation != simulation_clone

    for entity_id, entity in simulation.populations.items():
        assert entity != simulation_clone.populations[entity_id]

    assert simulation.persons != simulation_clone.persons

    salary_holder = simulation.person.get_holder("salary")
    salary_holder_clone = simulation_clone.person.get_holder("salary")

    assert salary_holder != salary_holder_clone
    assert salary_holder_clone.simulation == simulation_clone
    assert salary_holder_clone.population == simulation_clone.persons


def test_get_memory_usage(tax_benefit_system):
    simulation = SimulationBuilder().build_from_entities(
        tax_benefit_system, single
    )
    simulation.calculate("disposable_income", "2017-01")
    memory_usage = simulation.get_memory_usage(variables=["salary"])
    assert memory_usage["total_nb_bytes"] > 0
    assert len(memory_usage["by_variable"]) == 1


# TODO(SylviaDu99)
def test_version(tax_benefit_system):
    simulation = SimulationBuilder().build_from_entities(
        tax_benefit_system, single
    )

    cache = SimulationMacroCache(tax_benefit_system)
    assert cache.core_version == importlib.metadata.version(
        "policyengine-core"
    )
    assert cache.country_version == "0.0.0"


# Test set_cache_path
def test_set_cache_path(tax_benefit_system):
    cache = SimulationMacroCache(tax_benefit_system)
    cache.set_cache_path(
        parent_path="tests/core",
        dataset_name="test_dataset",
        variable_name="test_variable",
        period="2020",
        branch_name="test_branch",
    )
    cache.set_cache_value(
        cache_file_path=cache.cache_file_path,
        value=np.array([1, 2, 3], dtype=np.float32),
    )
    assert (
        str(cache.cache_file_path)
        == "tests/core/test_dataset_variable_cache/test_variable_2020_test_branch.h5"
    )


# Test set_cache_value

# Test get_cache_path

# Test get_cache_value

# Test clear_cache


def test_macro_cache(tax_benefit_system):
    simulation = SimulationBuilder().build_from_entities(
        tax_benefit_system,
        single,
    )
    simulation.calculate("disposable_income", "2017-01")
