import pytest

from ragger.error import ExceptionRAPDU
from application_client.response_unpacker import Errors
from enum import IntEnum

CLA: int = 0x5A

class InsType(IntEnum):
    GET_VERSION    = 0x00
    GET_PUBLIC_KEY = 0x01
    SIGN_HASH      = 0x02
    SIGN_TX        = 0x03
    SIGN_TXv1      = 0x04

# Ensure the app returns an error when a bad CLA is used
def test_bad_cla(backend):
    with pytest.raises(ExceptionRAPDU) as e:
        backend.exchange(cla=CLA + 1, ins=InsType.GET_VERSION)
    assert e.value.status == Errors.SW_CLA_NOT_SUPPORTED


# Ensure the app returns an error when a bad INS is used
def test_bad_ins(backend):
    with pytest.raises(ExceptionRAPDU) as e:
        backend.exchange(cla=CLA, ins=0xff)
    assert e.value.status == Errors.SW_INS_NOT_SUPPORTED


# Ensure the app returns an error when a bad P1 or P2 is used
def test_wrong_p1p2(backend):
    with pytest.raises(ExceptionRAPDU) as e:
        backend.exchange(cla=CLA, ins=InsType.GET_VERSION, p1=0xFF, p2=0x00)
    assert e.value.status == Errors.SW_WRONG_P1P2
    with pytest.raises(ExceptionRAPDU) as e:
        backend.exchange(cla=CLA, ins=InsType.GET_VERSION, p1=0x00, p2=0x80)
    assert e.value.status == Errors.SW_WRONG_P1P2
    #with pytest.raises(ExceptionRAPDU) as e:
    #    backend.exchange(cla=CLA, ins=InsType.GET_APP_NAME, p1=0xFF, p2=0x00)
    #assert e.value.status == Errors.SW_WRONG_P1P2
    #with pytest.raises(ExceptionRAPDU) as e:
    #    backend.exchange(cla=CLA, ins=InsType.GET_APP_NAME, p1=P1.P1_START, p2=P2.P2_MORE)
    #assert e.value.status == Errors.SW_WRONG_P1P2

# Ensure the app returns an error when a bad data length is used
def test_wrong_data_length(backend):
    # APDUs must be at least 4 bytes: CLA, INS, P1, P2.
    with pytest.raises(ExceptionRAPDU) as e:
        backend.exchange_raw(bytes.fromhex("E00300"))
    assert e.value.status == Errors.SW_WRONG_APDU_LENGTH
    # APDUs advertises a too long length
    with pytest.raises(ExceptionRAPDU) as e:
        backend.exchange_raw(bytes.fromhex("E003000005"))
    assert e.value.status == Errors.SW_WRONG_APDU_LENGTH


# Ensure there is no state confusion when trying wrong APDU sequences
# def test_invalid_state(backend):
#     with pytest.raises(ExceptionRAPDU) as e:
#         backend.exchange(cla=CLA,
#                          ins=InsType.SIGN_TX,
#                          p1=P1.P1_START + 1,  # Try to continue a flow instead of start a new one
#                          p2=P2.P2_MORE,
#                          data=b"abcde")  # data is not parsed in this case
#     assert e.value.status == Errors.SW_BAD_STATE
