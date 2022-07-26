import stim
from _builder import Builder


def main():
    builder = Builder.for_qubits([1, 1j, 2])
    builder.gate("H", [1, 1j, 2])
    print(builder.circuit)


if __name__ == '__main__':
    main()
