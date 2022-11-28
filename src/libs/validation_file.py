codes_operators = ["067", "068", "096", "097", "098", "050",
                           "066", "095", "099", "063", "073", "093"]



def phone_valid(phone_value):
        new_value = (phone_value.strip().
                     removeprefix('+').
                     replace("(", '').
                     replace(")", '').
                     replace("-", ''))
        if new_value[:2] == '38' and len(new_value) == 12 and new_value[2:5] in codes_operators:
            phone_value = new_value
            return new_value
