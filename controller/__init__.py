from controller.DeleteMessagesController import delete_messages_controller
from controller.OtherController import other_controller
from controller.PILController import pil_controller
from controller.MatsMessagesController import mats_messages_controller, init_mats_chat_messages_controller
from controller.TTSController import init_TTS_controller, TTS_controller

controllers = [
    delete_messages_controller,
    other_controller,
    pil_controller,
    TTS_controller,
    mats_messages_controller,
]

init_functions = [
    init_mats_chat_messages_controller,
    init_TTS_controller
]
