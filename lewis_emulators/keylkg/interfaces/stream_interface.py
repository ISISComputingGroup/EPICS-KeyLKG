from lewis.adapters.stream import StreamInterface, Cmd

from lewis_emulators.utils.command_builder import CmdBuilder
from lewis_emulators.utils.replies import conditional_reply

if_connected = conditional_reply('connected')
if_input_error = conditional_reply('input_correct', "ER,OF,00")


class KeylkgStreamInterface(StreamInterface):

    terminator = '\r'

    def __init__(self):

        super(KeylkgStreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self.commands = {
            CmdBuilder(self.set_communication_mode).escape("Q0").eos().build(),
            CmdBuilder(self.set_normal_mode).escape("R0").build(),
            CmdBuilder(self.set_offset).escape("SW,OF,").int().escape(",").float().eos().build(),
            CmdBuilder(self.get_offset).escape("SR,OF,").float().eos().build(),
            CmdBuilder(self.set_measurement_mode).escape("SW,HB,").int().escape(",").int().eos().build(),
            CmdBuilder(self.get_measurement_mode).escape("SR,HB,").int().eos().build(),
            CmdBuilder(self.get_value_output).escape("M").int().eos().build(),
            CmdBuilder(self.reset_output).escape("VR,").int().eos().build(),
        }

    @if_connected
    def reset_output(self, output):
        if output == 0:
            self.device.output1_raw_value = 0.0000
            self.device.output2_raw_value = 0.0000
            return "VR"
        elif output == 1:
            self.device.output1_raw_value = 0.0000
            return "VR"
        elif output == 2:
            self.device.output2_raw_value = 0.0000
            return "VR"

    @if_connected
    def get_value_output(self, output):
        # Example numbers to measure
        if output == 0:
            return "M0,{0},{1}".format(self.device.output1_value, self.device.output2_value)
        elif output == 1:
            return "M1,{0}".format(self.device.output1_value)
        elif output == 2:
            return "M2,{0}".format(self.device.output2_value)

    @if_connected
    def set_measurement_mode(self, head, function):
        if head == 1:
            self.device.head1_measurement_mode = function
        if head == 2:
            self.device.head2_measurement_mode = function
        return "SW,HB"

    @if_connected
    def get_measurement_mode(self, head):
        if head == 1:
            return "SR,HB,1,{0}".format(self.device.head1_measurement_mode)
        elif head == 2:
            return "SR,HB,2,{0}".format(self.device.head2_measurement_mode)

    @if_connected
    @if_input_error
    def set_offset(self, output, offset_value):
        if output == 0:
            self.device.output1_offset = offset_value
            self.device.output2_offset = offset_value
        elif output == 1:
            self.device.output1_offset = offset_value
        elif output == 2:
            self.device.output2_offset = offset_value
        return "SW,OF"

    @if_connected
    def get_offset(self, output):
        if output == 1:
            return "SR,OF,1,{0}".format(self.device.output1_offset)
        elif output == 2:
            return "SR,OF,2,{0}".format(self.device.output2_offset)

    @if_connected
    def set_communication_mode(self):
        self.device.mode = "SET-UP"
        return "Q0"

    @if_connected
    def set_normal_mode(self):
        self.device.mode = "MEASURE"
        return "R0"
