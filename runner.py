from classes import Machine, Vehicle
import json

VEHICLES_FN = 'vehicles.json'
CHANGE_FN = 'change.json'


def parse_vehicles():
    with open(VEHICLES_FN, 'r') as infile:
        vehicles_json = json.load(infile)

    return [
        (Vehicle(int(id), value['name'], value['price'], value['mileage']), value['stock'])
        for id, value in vehicles_json.items()
    ]


def parse_change():
    with open(CHANGE_FN, 'r') as infile:
        change_json = json.load(infile)

    change = []

    for coin in change_json:
        change.append((coin['value'], coin['number']))

    return change


if __name__ == '__main__':
    machine = Machine()

    for (vehicle, stock) in parse_vehicles():
        machine.add_vehicle(vehicle, stock)

    for (value, number) in parse_change():
        machine.add_change(value, number)

    while True:
        print(machine.get_options())
        option = input('Enter your option: ')
        print('')

        if machine.is_valid_option(option):
            if Machine.is_rent_option(option):
                command, vehicle = option.split()
                if not machine.start_sale(vehicle):
                    print('The vehicle you have chosen is sold out.')
                    print('')
                    continue

                while not machine.is_enough_money():
                    current_sale_info = machine.get_current_sale_info()
                    print(f'You choose vehicle {machine.get_vehicle_info(vehicle)}')
                    coin = input(f'Insert money (€{current_sale_info.paid} of €{current_sale_info.price}): ')
                    machine.insert_coin(coin)

                change = machine.finish_sale()

                if change is None:
                    while not Machine.is_cancel_option(option) and not Machine.is_finish_option(option):
                        message = f"Not enough change {machine.total_change()} or the coins available don't match " \
                                  f"the change.\nYou can either Cancel (C) or Finish (F) without change: "

                        print(machine.cashier.change)
                        option = input(message)

                        if Machine.is_cancel_option(option):
                            machine.cancel_sale()
                        elif Machine.is_finish_option(option):
                            machine.finish_sale(force=True)
                        else:
                            print('Please enter a valid option.')

            elif Machine.is_reload_vehicles_option(option):
                for (vehicle, stock) in parse_vehicles():
                    machine.add_vehicle(vehicle, stock)

            elif Machine.is_reload_change_option(option):
                for (value, number) in parse_change():
                    machine.add_change(value, number)

            elif Machine.is_list_option(option):
                print(machine.get_list())

            elif Machine.is_info_option(option):
                command, vehicle = option.split()
                print(machine.get_vehicle_info(vehicle))

            elif Machine.is_help_option(option):
                continue

            elif Machine.is_return_option(option):
                command, vehicle, mileage = option.split(' ')
                machine.return_vehicle(vehicle, mileage)

            else:
                print(f'{option} is not a valid option.')

        print('')

