# Compatibility layer

CPU memory, peripheral, interrupt, panel, MIDI, and storage adaptation belongs here once a measured boot trace establishes the contract. Keep each shim tied to a compatibility-matrix row and a test. Avoid duplicating Machinedrum firmware behavior in host code when the original firmware can execute it.
