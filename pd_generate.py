import random
import pandas as pd

def data_role() -> pd.DataFrame:
    user_ids = [random.randint(1000,9999) for _ in range(10)]
    role_name = [random.choice(['Employee','Operator','Administrator','Guest']) for _ in range(10)]

    sv_to_dict = {
        'user_ids': user_ids,
        'role_name': role_name
    }

    sv_data = pd.DataFrame(sv_to_dict)
    # print(sv_data)
    dt_role = sv_data.to_dict()
    return dt_role

def data_tickets() -> pd.DataFrame:
    ticket_numbers = [f"CRQ{'0'*5}{i:04d}" for i in range(1,11)]
    sv_to_dict = {
        'ticket_numbers': ticket_numbers,
    }
    sv_data = pd.DataFrame(sv_to_dict)
    list_tickets = sv_data['ticket_numbers'].tolist()
    return list_tickets

# df = data_role()
# print(df)
