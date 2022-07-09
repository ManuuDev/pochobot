from threading import Timer

from .ErrorHandler import PollError
from .Utils import strip_strings_from_list


class Poll:
    response_content: str
    question: str
    list_of_options: str
    ammount_of_options: int
    author_id: int
    options_with_counter: list
    current_poll_message: object
    timer: Timer

    def __init__(self):
        self.options_with_counter = list()
        pass

    def fill(self, question, list_of_options):
        self.question = question
        self.list_of_options = list_of_options
        self.ammount_of_options = len(list_of_options)
        string_of_options: str = ''

        for counter, option in enumerate(list_of_options, start=1):
            string_of_options += '\n\t{}) {}'.format(counter, option)

        self.response_content = 'Votacion iniciada: \nPregunta: {0}?\nOpciones: {1}'.format(
            question, string_of_options)

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.cancel()


pollStarted: bool = False
currentPoll: Poll


async def startpoll(ctx, text):
    global pollStarted, currentPoll

    if not pollStarted:
        pollStarted = True

        currentPoll = Poll()

        currentPoll.author_id = ctx.message.author.id

        first_split = text.strip().split('?', 1)
        list_of_options: list

        if len(first_split) > 1:
            list_of_options = first_split[1].split(',')
            list_of_options = strip_strings_from_list(list_of_options)
        else:
            clean_poll()
            raise PollError(
                'Error en el formato, deberia ser: pregunta? opcion1, opcion2, opcion3, ...')

        ammount_of_options = len(list_of_options)
        if 1 < ammount_of_options <= 9:
            question = first_split[0]
            for option in list_of_options:
                currentPoll.options_with_counter.append([option, 0])

            try:
                await ctx.message.delete(delay=1)
            except:
                pass

            currentPoll.fill(question, list_of_options)
            return currentPoll
        else:
            clean_poll()
            raise PollError('Tenes que poner entre una y nueve opciones')
    else:
        raise PollError('Hay una votacion en curso, espera tu turno papito...')


def add_vote_with_index(index, ammount):
    global currentPoll
    option = currentPoll.options_with_counter[index]
    option[1] += ammount


def clean_poll():
    global pollStarted, currentPoll
    try:
        currentPoll.stop_timer()
    except:
        pass

    pollStarted = False


async def endpoll(ctx, timeout=False):
    global currentPoll

    if ctx.author.id != currentPoll.author_id and not timeout:
        raise PollError('Solo el autor de la votacion puede finalizarla')

    if not timeout:
        currentPoll.stop_timer()

    message = await currentPoll.current_poll_message.channel.fetch_message(currentPoll.current_poll_message.id)
    index = 0
    for reaction in message.reactions:
        add_vote_with_index(index, reaction.count)
        index += 1

    response = ''
    for option in currentPoll.options_with_counter:
        option[1] = option[1] - 1
        response += 'Opcion: {0} tiene: {1} votos\n'.format(
            option[0], option[1])

    winning_option = max(currentPoll.options_with_counter,
                         key=lambda item: item[1])

    tie = all(x[1] == winning_option[1]
              for x in currentPoll.options_with_counter)

    if tie:
        response += '\nEmpate en el resultado'
    else:
        response += '\nResultado ganador: {0}'.format(winning_option[0])

    clean_poll()

    return response
