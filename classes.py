from typing import NamedTuple, Union


class Vehicle(object):
    def __init__(self, id: int, name: str, price: float, mileage: int):
        self.id = id
        self.name = name
        self.price = price
        self.mileage = mileage

    def __str__(self):
        return f'{self.id} - {self.name} - €{self.price} - {self.mileage}km'


class CurrentSaleInfo(NamedTuple):
    paid: float
    price: float


class Cashier:
    VALID_COINS = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0]

    def __init__(self):
        self._change = {}
        self._total_sold = 0.0
        self.current_amount = 0.0

    def add_change(self, coin_value: Union[str, float], number: Union[str, int]) -> None:
        """
        Populate the available change by adding a coin value and the number of coins available
        """
        try:
            self._change[float(coin_value) * 100] = int(number)
        except ValueError:
            print('Cannot insert change.')
            raise

    def calculate_change(self, price: float) -> float:
        """
        Check if the coins available are enough or fit the change needed
        """

        change = self.current_amount - price
        change_to_calculate = change

        if change_to_calculate == 0.0:
            return change

        if self.total_change * 100 < change_to_calculate:
            return None

        for value in reversed(self.VALID_COINS):
            number_coins_needed = int(change_to_calculate / value)
            if number_coins_needed != 0 and self._change[value] != 0:
                if number_coins_needed <= self._change[value]:
                    self._change[value] -= number_coins_needed
                    change_coin_available = value * number_coins_needed
                else:
                    change_coin_available = value * self._change[value]
                    self._change[value] = 0

                change_to_calculate -= change_coin_available

            if change_to_calculate == 0.0:
                return change

        return None

    def insert_coin(self, coin_value: str) -> None:
        """
        Simulate the coin inserted by the customer/buyer
        """
        try:
            self.current_amount += float(coin_value)
        except ValueError:
            print('Invalid coin.')
            raise

    def finish_sale(self) -> None:
        """
        Close a sale and reset the current sale state
            (total sold so far and the current amount inserted tracker)
        """
        self._total_sold += self.current_amount
        self.current_amount = 0.0

    def cancel_sale(self) -> None:
        """
        Cancel a sale which means reset the current amount inserted tracker
        """
        self.current_amount = 0.0

    @property
    def total(self) -> float:
        """
        Total amount collected over the cashier lifetime (resets when "switched off")
        """
        return self._total_sold

    @property
    def total_change(self) -> float:
        """
        The total amount of change available
        """
        return sum([value * number for value, number in self._change.items()])

    @property
    def change(self) -> dict:
        """
        The actual change available in terms of coins
        """
        return self._change


class Machine:

    def __init__(self):
        self.stock = {}
        self.cashier = Cashier()
        self.current_sale = None
        self.rented = {}
        self.options = {
            'rv': 'Reload Vehicle Stock',
            'rc': 'Reload Change',
            'help': 'All options',
            'list': 'List all vehicles a_update_listvailable',
            'info': 'Info about vehicle with [id]',
            'rent': 'Rent a vehicle with [id]',
            'return': 'Return a vehicle [id] with [mileage]'
        }

    def add_vehicle(self, vehicle: Vehicle, stock: int) -> None:
        """
        Add a vehicle to the machine stock
        """
        if isinstance(vehicle, Vehicle):
            self.stock[vehicle.id] = {
                'vehicle': vehicle,
                'stock': stock
            }

    def add_change(self, coin_value: float, number: int) -> None:
        """
        Used as a proxy to add change to the cashier
        """
        self.cashier.add_change(coin_value, number)

    def start_sale(self, option: str) -> bool:
        """
        Set the current sale as the vehicle the user has chosen
        """
        option = int(option)

        if self.stock[option]['stock'] == 0:
            return False

        self.current_sale = self.stock[int(option)]['vehicle']

        return True

    def insert_coin(self, value: str) -> None:
        """
        Simulate the coin inserted by the customer/buyer
        """
        if self.current_sale is None:
            print('Please select a vehicle first.')
            return

        self.cashier.insert_coin(value)

    def is_enough_money(self) -> bool:
        """
        Check if the amount inserted by the customer is enough
        """
        if self.current_sale is None:
            return False

        return self.cashier.current_amount >= self.current_sale.price

    def finish_sale(self, force: bool = False) -> float:
        """
        Finish a sale when there is change available or is forced to finish

        A sale can be forced to finish if there is no change but the buyer still wants the rent
            the vehicle
        """
        change = self.cashier.calculate_change(self.current_sale.price)

        if change is not None or force:
            print(f'\nYou just bought a {self.current_sale.name} and '
                  f'got €{change if change is not None else 0.0} change.')

            self.stock[self.current_sale.id]['stock'] -= 1
            self.rented[self.current_sale.id] = self.current_sale
            self.current_sale = None
            self.cashier.finish_sale()

        return change

    def return_vehicle(self, vehicle_id: str, mileage: str):
        """
        Return a vehicle with new mileage
        """
        try:
            vehicle = self.rented[int(vehicle_id)]
            if int(mileage) <= vehicle.mileage:
                print('A vehicle returned cannot have less/equal mileage.')
                return
        except KeyError:
            print(f'Vehicle {vehicle_id} is not rented')
            return

        self.stock[int(vehicle_id)]['stock'] += 1
        self.stock[int(vehicle_id)]['vehicle'].mileage = int(mileage)
        self.rented.pop(int(vehicle_id))

        print(f'Vehicle {vehicle_id} returned successfully with new mileage {mileage}')

    def cancel_sale(self) -> None:
        """
        Cancel a sale in the case there is no change and the user does not want to rent the vehicle
        """
        self.current_sale = None
        self.cashier.cancel_sale()

    def get_current_sale_info(self) -> CurrentSaleInfo:
        """
        The amount paid by the buyer and the selected vehicle price
        """
        return CurrentSaleInfo(self.cashier.current_amount, self.current_sale.price)

    def get_options(self) -> str:
        """
        A string representation of the option (menu) the user can select from
        """
        return '\n'.join([f'{command} - {description}' for command, description in self.options.items()])

    def get_list(self) -> str:
        """
        A string representation of the options (menu) the user can select from
        """
        return '\n'.join([f'{vehicles["vehicle"]} - (Stock: {vehicles["stock"]})' for vehicles in self.stock.values()])

    def get_vehicle_info(self, vehicle_id: str) -> str:
        """
        A string representation of the vehicle
        """
        vehicle = self.stock.get(int(vehicle_id), None)

        if vehicle:
            return f'{vehicle["vehicle"]}'

        return f'No vehicle with ID {vehicle_id} found.'

    def is_valid_option(self, option: str) -> bool:
        """
        Checks if the option inserted by the user is valid
        """
        return option.split(' ')[0].lower() in self.options

    def total_change(self) -> bool:
        """
        The total change available in the cashier
        """
        return self.cashier.total_change

    @staticmethod
    def is_rent_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is to rent a vehicle
        """
        try:
            command, vehicle = option.split(' ')
            int(vehicle)
        except ValueError:
            return False

        return command == 'rent'

    @staticmethod
    def is_cancel_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is cancel
        """
        return option.lower() == 'c'

    @staticmethod
    def is_finish_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is finish
        """
        return option.lower() == 'f'

    @staticmethod
    def is_reload_vehicles_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is to reload the vehicle stock
        """
        return option.lower() == 'rv'

    @staticmethod
    def is_reload_change_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is to reload the change available
        """
        return option.lower() == 'rc'

    @staticmethod
    def is_list_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is to list all vehicle
        """
        return option.lower() == 'list'

    @staticmethod
    def is_info_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is to get vehicle info
        """
        try:
            command, vehicle = option.split(' ')
            int(vehicle)
        except ValueError:
            return False

        return command.lower() == 'info'

    @staticmethod
    def is_help_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is to list all options
        """
        return option.lower() == 'help'

    @staticmethod
    def is_return_option(option: str) -> bool:
        """
        Checks if the option inserted by the user is to return
        """
        try:
            command, vehicle, mileage = option.split(' ')
            int(vehicle)
        except ValueError:
            return False

        return command.lower() == 'return'
