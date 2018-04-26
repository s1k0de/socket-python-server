# Модуль отвечающий за вычисления

def is_digit_element_list(arg):
    try:
        float(arg)
        return True
    except ValueError:
        return False

def divide(element1, element2):

    if is_digit_element_list(element1) and is_digit_element_list(element2):
        try:
            answer = str(float(element1)/float(element2))

        except ZeroDivisionError:
            answer = "Деление на ноль"
            return answer

        else:
            return answer

    else:
        return "Нельзя поделить"