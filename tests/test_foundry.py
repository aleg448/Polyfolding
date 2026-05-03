from crystalprobe.foundry.adapters import all_adapter_availability, check_adapter_availability


def test_adapter_availability_reports_known_backends():
    names = {availability.name for availability in all_adapter_availability()}
    assert {"ase_cif", "mace_off", "aimnet2", "uma", "fastcsp"}.issubset(names)


def test_missing_adapter_has_blocker_or_is_available():
    availability = check_adapter_availability("ase_cif")
    assert availability.available or availability.blocker is not None

