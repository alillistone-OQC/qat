from __future__ import annotations

from typing import Optional

from pydantic import Field

from qat.model.component import Component
from qat.model.serialisation import Ref, RefDict, RefList
from qat.purr.compiler.devices import ChannelType


class PhysicalBaseband(Component):
    """
    Models the Local Oscillator (LO) used with a mixer to change the
    frequency of a carrier signal.
    Attributes:
        frequency: The frequency of the LO.
        if_frequency: The intermediate frequency (IF) resulting from
                      mixing the baseband with the carrier signal.
    """

    frequency: float = Field(ge=0.0)
    if_frequency: Optional[float] = Field(ge=0.0, default=250e6)


class PhysicalChannel(Component):
    """
    Models a physical channel that can carry one or multiple pulses.
    Attributes:
        baseband: The physical baseband.
        sample_time: The rate at which the pulse is sampled.
        block_size: The number of samples within a single block.
        phase_iq_offset: Deviation of the phase difference of the I
                         and Q components from 90° due to imperfections
                         in the mixing of the LO and unmodulated signal.
        bias: The bias in voltages V_I / V_Q for the I and Q components.
        acquire_allowed: If the physical channel allows acquire pulses.
    """

    baseband: Ref[PhysicalBaseband] = Field(frozen=True)

    sample_time: float = Field(ge=0.0)
    block_size: Optional[int] = Field(ge=1, default=1)
    phase_iq_offset: float = 0.0
    bias: float = 1.0
    acquire_allowed: bool = False


class PulseChannel(Component):
    """
    Models a pulse channel on a particular device.
    Attributes:
        physical_channel: Physical channel that carries the pulse.
        frequency: Frequency of the pulse.
        bias: Mean value of the signal, quantifies offset relative to zero mean.
        scale: Scale factor for mapping the voltage of the pulse to frequencies.
        fixed_if: Flag which determines if the intermediate frequency is fixed.
        channel_type: Type of the pulse.
        auxiliary_qubits: Any extra devices this PulseChannel could be affecting except
                           the current one. For example in cross resonance pulses.
    """

    physical_channel: Ref[PhysicalChannel]

    frequency: float = Field(ge=0.0, default=0.0)
    bias: complex = 0.0 + 0.0j
    scale: complex = 1.0 + 0.0j
    fixed_if: bool = False

    channel_type: Optional[ChannelType] = Field(frozen=True, default=None)
    auxiliary_qubits: RefList[Qubit] = []


class QuantumDevice(Component):
    """
    A physical device whose main form of operation involves pulse channels.
    Attributes:
        pulse_channels: Pulse channels with their ids as keys.
        physical_channel: Physical channel associated with the pulse channels.
                          Note that this physical channel must be equal to the
                          physical channel associated with the pulse channels.
        default_pulse_channel_type: Default type of pulse for the quantum device.
    """

    pulse_channels: RefDict[PulseChannel] = Field(frozen=True)
    physical_channel: Ref[PhysicalChannel] = Field(frozen=True)

    default_pulse_channel_type: ChannelType = Field(
        frozen=True, default=ChannelType.measure
    )


class Resonator(QuantumDevice):
    """Models a resonator on a chip. Can be connected to multiple qubits."""

    pass


class Qubit(QuantumDevice):
    """
    Models a superconducting qubit on a chip, and holds all information relating to it.
    Attributes:
        measure_device: The resonator coupled to the qubit.
        index: The index of the qubit on the chip.
        measure_amp: Amplitude for the measure pulse.
        default_pulse_channel_type: Default type of pulse for the qubit.
    """

    measure_device: Ref[Resonator] = Field(frozen=True)

    index: int = Field(ge=0)
    measure_amp: float = 1.0
    default_pulse_channel_type: ChannelType = Field(frozen=True, default=ChannelType.drive)

    coupled_qubits: Optional[RefList[Qubit]] = None

    def __repr__(self):
        return f"Q{self.index}"