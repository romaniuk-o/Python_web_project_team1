from collections import UserDict
import shelve


class Note:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'


class Tag:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'


class NoteRecord(UserDict):
    def __init__(self, note: Note, tag: Tag = None):
        self.note = note
        self.tags = []
        if tag:
            self.tags.append(tag)

    def __repr__(self):
        if len(self.tags) > 0:
            return f'Tags: {[t.value for t in self.tags]}\n{self.note.value}'
        return f'{self.note.value}'

    def add_tag(self):
        while True:
            tag_input = input('Please, add tag name or skip:')
            my_tag = Tag(tag_input)
            if tag_input == "":
                break
            if my_tag.value not in [t.value for t in self.tags]:
                self.tags.append(my_tag)


class Notebook(UserDict):

    def __init__(self):
        self.data = {}

    def __repr__(self):
        return f'{self.data}'

    def add_note(self, note: Note):
        my_note = Note(note)
        rec = NoteRecord(my_note)
        self.data[rec.note.value] = rec
        return rec.add_tag()

    def delete_note(self, rec: NoteRecord):
        for k, v in self.data.items():
            # if isinstance(v, NoteRecord):
            if v.note == rec.note:
                deleted_note = v.note
                self.data.pop(k)
                return deleted_note

    def save_to_file(self):
        with shelve.open(filename) as db:
            db['NoteBook'] = self.data

    def get_tags(self):
        tags_list = []
        for rec in self.values():
            for t in rec.tags:
                tags_list.append(str(t))
        if len(tags_list) > 0:
            tags_set = sorted(set(tags_list), reverse=False)
            return tags_set
        else:
            return None


def input_error_note(func):
    def inner(*args):
        try:
            return func(*args)
        except KeyError:
            return 'No records found'
        except IndexError:
            return 'No tags records in the notebook.'
        except ValueError:
            return 'Search the note first.'
        except TypeError:
            return 'Note changed'

    return inner


def load(my_filename):
    try:
        with shelve.open(my_filename) as db:
            notebook.data = db['NoteBook']
    except KeyError:
        with shelve.open(my_filename) as db:
            db['NoteBook'] = notebook


def add_note(note: Note):
    notebook.add_note(note)
    notebook.save_to_file()
    return 'Note added'


@input_error_note
def show_all(*args):
    notes_list = [v for v in notebook.values()]
    global last_search
    last_search = notes_list
    result = ''
    if len(notes_list) == 0:
        raise KeyError
    for num, item in enumerate(notes_list, 1):
        result += f'{num} {item}\n'
    return result.strip()


@input_error_note
def search(search_info):
    search_output = []
    search_output_rec = []
    result = ''
    if search_info.lower().startswith('by tag'):
        search_tag = search_info[7:].strip()
        for rec in notebook.values():
            for t in rec.tags:
                if search_tag in str(t):
                    search_output.append(rec.note)
                    search_output_rec.append(rec)
    else:
        for rec in notebook.values():
            if search_info in str(rec.note):
                search_output.append(rec)
                search_output_rec.append(rec)
            for t in rec.tags:
                if search_info in str(t):
                    search_output.append(rec)
                    search_output_rec.append(rec)
    if len(search_output) == 0:
        raise KeyError
    global last_search
    last_search = search_output_rec
    for num, item in enumerate(search_output, 1):
        result += f'{num}   {item}\n'
    return result.strip()


@input_error_note
def change(my_input):
    commands = my_input.split(' ')
    num = commands[0]
    new_note = Note(my_input[len(num):].strip())
    global last_search
    if not last_search:
        raise ValueError
    if int(num) > 0 and len(new_note.value) > 0:
        counter = 1
        for item in last_search:
            if counter == int(num):
                item.note = new_note
                item.add_tag()
            counter += 1
        last_search = []
        notebook.save_to_file()
        raise TypeError
    else:
        return 'Please, enter number of the note you want to change followed by the new note text.'


def bot_help(*args):
    return """
    The following functions are available in the Notebook:
    "add note [note text]" - create a new note with follow up tag request.
    "delete note [number]" - delete note by the number from the previous search results 
    from show all or search function."help" - see all available commands.
    "change note [number] [new note text]" - change note by the number from the previous search results 
    from show all or search function to new note. Tags change will follow.
    "show all" - Show all notes records with tags.
    "tags" - show all saved tags. 
    "search note [text]" - Search notes and tags by text.
    "search note by tag [text]" - Search tags only by text.
    "sort notes" - Sort notes by tags.
    "good bye", "close", "exit" - exit from the bot.
    """


@input_error_note
def delete(del_num):
    global last_search
    if not last_search:
        raise ValueError
    counter = 1
    for item in last_search:
        if counter == int(del_num):
            result = notebook.delete_note(item)
            last_search = []
            notebook.save_to_file()
            return f'Note: "{result}" deleted.'
        counter += 1


@input_error_note
def show_tags(*args):
    result = notebook.get_tags()
    if result:
        return ','.join(result)
    else:
        raise IndexError


@input_error_note
def sort_notes(*args):
    tags = notebook.get_tags()
    no_tag_list = []
    sort_result = {}
    for t in tags:
        sort_result[t] = []
        for rec in notebook.values():
            if not rec.tags:
                no_tag_list.append(rec.note.value)
            for tag in rec.tags:
                if t == str(tag):
                    sort_result[t].append(rec.note.value)
    sort_result['no tag'] = set(no_tag_list)
    result = ""
    for k, v in sort_result.items():
        result += f'\n{k}:\n'
        for value in v:
            result += f'{value}\n'
    return result.strip()


def func_exit(*args):
    return 'Good bye!'


notebook = Notebook()
filename = 'some_db'
last_search = []
COMMANDS = {search: ["search note"],
            func_exit: ["good bye", "close", "exit", "."],
            add_note: ["add note"],
            show_all: ["show all"],
            change: ["change note"],
            bot_help: ["help"],
            delete: ["delete note"],
            show_tags: ['tags'],
            sort_notes: ['sort notes']
            }


def parse_command(user_input: str):
    for code_function, input_function in COMMANDS.items():
        for i in input_function:
            if user_input.lower().startswith(i.lower()):
                note = user_input[len(i):].strip()
                return [code_function, note]
    return 'Unknown command'


def main():
    load(filename)
    while True:
        user_input = input("Please, enter command: ")  # add note, search notes
        user_command = parse_command(user_input)
        if user_command == 'Unknown command':
            continue
        result = user_command[0](user_command[1])
        print(result)
        if result == 'Good bye!':
            break


if __name__ == "__main__":
    main()
