from threading import Timer

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

        self.response_content = 'Votacion iniciada: \nPregunta: {0}?\nOpciones: {1}'.format(question, string_of_options)

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.cancel()
