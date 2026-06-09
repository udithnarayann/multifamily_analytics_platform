from datetime import date
from decimal import Decimal

from app.services.freddie_mac_mlp_mapper import (
    label_mortgage_status,
    map_mlp_csv_row_to_observation,
    parse_optional_date,
    parse_optional_decimal,
    parse_optional_int,
)


def sample_row() -> dict[str, str]:
    return {
        "": "0",
        "lnno": "418251002",
        "quarter": "y00q1",
        "mrtg_status": "100.0",
        "amt_upb_endg": "11260166.52",
        "liq_upb_amt": "",
        "dt_fund": "1999-09-30",
        "amt_upb_pch": "11300000.0",
        "dealname": "NONE",
        "rate_ltv": "0.79718",
        "rate_dcr": "1.268",
        "code_int": "FIX",
        "rate_int": "0.0782",
        "cd_fxfltr": "",
        "cnt_amtn_per": "360.0",
        "cnt_blln_term": "120.0",
        "cnt_io_per": "0.0",
        "cnt_mrtg_term": "120",
        "cnt_rsdntl_unit": "264.0",
        "cnt_yld_maint": "114.0",
        "code_sr": "",
        "dt_io_end": "",
        "dt_mty": "2009-10-01",
        "geographical_region": "ATLANTA, GA",
        "code_st": "GA",
        "securitized": "",
        "PreFcl_FCL_ExpInc": "",
        "REO_Operating_ExpInc": "",
        "dt_sold": "",
        "Sales_Price": "",
        "Selling_ExpInc": "",
        "credit_loss": "",
        "liq_dte": "",
        "id_link_grp": "201.0",
        "lien_number": "First Mortgage",
        "flag_defeased": "",
    }


def test_numeric_and_integer_parsing() -> None:
    assert parse_optional_decimal("1,234.56") == Decimal("1234.56")
    assert parse_optional_decimal("") is None
    assert parse_optional_int("100.0") == 100
    assert parse_optional_int("") is None


def test_date_parsing_supports_iso_and_sas_style_dates() -> None:
    assert parse_optional_date("1999-09-30") == date(1999, 9, 30)
    assert parse_optional_date("30SEP1999") == date(1999, 9, 30)
    assert parse_optional_date("") is None


def test_status_code_labeling() -> None:
    assert label_mortgage_status("100.0") == "current_or_less_than_60_days_delinquent"
    assert label_mortgage_status("200") == "60_or_more_days_delinquent"
    assert label_mortgage_status("250") == "modification_with_loss"
    assert label_mortgage_status("300") == "foreclosure"
    assert label_mortgage_status("450") == "real_estate_owned"
    assert label_mortgage_status("500") == "closed"
    assert label_mortgage_status("") is None


def test_maps_csv_row_and_ignores_leading_unnamed_index_column() -> None:
    mapped = map_mlp_csv_row_to_observation(sample_row(), source_file="mlpd.csv")

    assert mapped.loan_id == "418251002"
    assert mapped.reporting_quarter == "y00q1"
    assert mapped.mortgage_status_code == 100
    assert mapped.ending_balance == Decimal("11260166.52")
    assert mapped.original_balance == Decimal("11300000.0")
    assert mapped.original_ltv == Decimal("0.79718")
    assert mapped.original_dcr == Decimal("1.268")
    assert mapped.note_rate == Decimal("0.0782")
    assert mapped.fund_date == date(1999, 9, 30)
    assert mapped.maturity_date == date(2009, 10, 1)
    assert mapped.residential_units == 264
    assert mapped.property_state == "GA"
    assert mapped.property_metro == "ATLANTA, GA"
    assert mapped.link_id_indicator == 201
    assert mapped.lien_number == "First Mortgage"
    assert mapped.source_file == "mlpd.csv"
    assert "" not in mapped.raw_row_payload
    assert mapped.raw_row_payload["lnno"] == "418251002"
