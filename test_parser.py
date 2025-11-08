import os
import re

class TestParser:
    def __init__(self, data_folder="test_data"):
        self.data_folder = data_folder
        self.tests_cache = {}

    def parse_task_619(self, content):
        tests = {}
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if line.isdigit():
                test_num = int(line)
                i += 1

                if i < len(lines) and 'input' in lines[i].lower():
                    i += 1
                
                if i < len(lines):
                    size = int(lines[i].strip())
                    i += 1

                matrix = []
                for j in range(size):
                    if i < len(lines):
                        matrix.append(lines[i].strip())
                        i += 1

                while i < len(lines) and (not lines[i].strip() or 'output' in lines[i].lower()):
                    i += 1

                output_lines = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                    output_lines.append(lines[i].strip())
                    i += 1

                tests[test_num] = {
                    'input': f"{size}\n" + "\n".join(matrix),
                    'output': "\n".join(output_lines)
                }

            else:
                i += 1

        return tests
    
    def parse_task_3580(self, content):
        tests = {}
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if line.isdigit():
                test_num = int(line)
                i += 1

                if i < len(lines) and 'input' in lines[i].lower():
                    i += 1

                input_lines = []
                while i < len(lines) and lines[i].strip() and 'output' not in lines[i].lower():
                    input_lines.append(lines[i].strip())
                    i += 1

                if i < len(lines) and 'output' in lines[i].lower():
                    i += 1

                output_lines = []
                while i < len(lines) and lines[i].strip() and lines[i].strip().isdigit():
                    output_lines.append(lines[i].strip())
                    i += 1

                tests[test_num] = {
                    'input': "\n".join(input_lines),
                    'output': "\n".join(output_lines)
                }

            else:
                i += 1

        return tests
    
    def load_all_tests(self):
        all_tests = {}

        try:
            with open(os.path.join(self.data_folder, 'ex-619.txt'), 'r', encoding='utf-8') as f:
                content = f.read()
                all_tests[619] = self.parse_task_619(content)

        except FileNotFoundError:
            print("Файл для задачи 619 не найден")

        try:
            with open(os.path.join(self.data_folder, 'ex-3580.txt'), 'r', encoding='utf-8') as f:
                content = f.read()
                all_tests[3580] = self.parse_task_3580(content)

        except FileNotFoundError:
            print("Файл для задачи 3580 не найден")

        self.tests_cache = all_tests  # Добавлено!
        return all_tests

    def get_test_data(self, task_id, test_number):
        if not self.tests_cache:
            self.load_all_tests()

        task_id = int(task_id)
        test_number = int(test_number)

        if task_id in self.tests_cache and test_number in self.tests_cache[task_id]:
            return self.tests_cache[task_id][test_number]
        return None