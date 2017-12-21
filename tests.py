from classes import Cashier, CurrentSaleInfo, Machine, Vehicle
from unittest import TestCase


class TestCashier(TestCase):

    def setUp(self):
        self.cashier = Cashier()
        self.cashier.add_change(0.01, 0)
        self.cashier.add_change(0.02, 0)
        self.cashier.add_change(0.05, 0)
        self.cashier.add_change(0.10, 0)
        self.cashier.add_change(0.20, 0)
        self.cashier.add_change(0.50, 0)
        self.cashier.add_change(1.0, 0)
        self.cashier.add_change(2.0, 0)
        self.cashier.add_change(5.0, 0)

    def test_add_change_invalid(self):
        with self.assertRaises(ValueError):
            self.cashier.add_change('test', 100)
            self.cashier.add_change(10, 'test')

        self.assertTrue(all([val == 0 for val in self.cashier.change.values()]))

    def test_add_change(self):
        coin_value = 10.0
        number = 100

        self.cashier.add_change(coin_value, number)

        self.assertTrue(coin_value * 100 in self.cashier.change)
        self.assertEquals(self.cashier.change[coin_value * 100], 100)

    def test_insert_coin_invalid(self):
        with self.assertRaises(ValueError):
            self.cashier.insert_coin('d')

        self.assertEquals(self.cashier.current_amount, 0.0)

    def test_insert_coin(self):
        coin_value = 10.0

        self.cashier.insert_coin(coin_value)

        self.assertEquals(self.cashier.current_amount, coin_value)

    def test_finish_sale(self):
        coin_value = 10.0

        self.cashier.insert_coin(coin_value)

        self.assertEquals(self.cashier.current_amount, coin_value)

        self.cashier.finish_sale()

        self.assertEquals(self.cashier.current_amount, 0.0)
        self.assertEquals(self.cashier.total, 10.0)

    def test_cancel_sale(self):
        coin_value = 10.0

        self.cashier.insert_coin(coin_value)

        self.assertEquals(self.cashier.current_amount, coin_value)

        self.cashier.cancel_sale()

        self.assertEquals(self.cashier.current_amount, 0.0)
        self.assertEquals(self.cashier.total, 0.0)

    def test_calculate_change_no_change(self):
        self.cashier.insert_coin(10.0)

        self.assertEqual(self.cashier.calculate_change(5.0), None)

    def test_calculate_change_no_coins_match(self):

        self.cashier.insert_coin(2)

        self.assertEqual(self.cashier.calculate_change(0.97), None)

    def test_calculate_change(self):
        self.cashier.add_change(0.01, 2)

        self.cashier.insert_coin(5)

        self.assertEqual(self.cashier.calculate_change(3.0), 2.0)


class TestMachine(TestCase):
    def setUp(self):
        self.machine = Machine()
        self.vehicle = Vehicle(1, 'Test Vehicle', 10, 100)
        self.machine.cashier.add_change(0.01, 1)
        self.machine.cashier.add_change(0.02, 1)
        self.machine.cashier.add_change(0.05, 1)
        self.machine.cashier.add_change(0.10, 1)
        self.machine.cashier.add_change(0.20, 1)
        self.machine.cashier.add_change(0.50, 1)
        self.machine.cashier.add_change(1.0, 1)
        self.machine.cashier.add_change(2.0, 1)
        self.machine.cashier.add_change(5.0, 1)

    def test_add_vehicle_invalid(self):
        vehicle = 'blah'

        self.machine.add_vehicle(vehicle, 10)

        self.assertEquals(len(self.machine.stock), 0)

    def test_add_vehicle(self):
        stock = 10
        self.machine.add_vehicle(self.vehicle, stock)

        self.assertEquals(len(self.machine.stock), 1)
        self.assertTrue(self.vehicle.id in self.machine.stock)
        self.assertTrue(self.machine.stock[self.vehicle.id], stock)

    def test_is_enough_money_no_sale(self):
        self.machine.insert_coin(10)

        self.assertFalse(self.machine.is_enough_money())

    def test_is_enough_money(self):
        self.machine.add_vehicle(self.vehicle, 10)
        self.machine.start_sale(self.vehicle.id)
        self.machine.insert_coin(10)

        self.assertTrue(self.machine.is_enough_money())

    def test_cancel_sale(self):
        self.machine.add_vehicle(self.vehicle, 10)
        self.machine.start_sale(self.vehicle.id)
        self.machine.insert_coin(2)

        self.assertTrue(self.machine.current_sale is not None)
        self.assertTrue(self.machine.cashier.current_amount != 0.0)

        self.machine.cancel_sale()

        self.assertTrue(self.machine.current_sale is None)
        self.assertTrue(self.machine.cashier.current_amount == 0.0)

    def test_get_choices(self):
        options = 'rv - Reload Vehicle Stock\n' \
                  'rc - Reload Change\n' \
                  'help - All options\n' \
                  'list - List all vehicles available\n' \
                  'info - Info about vehicle with [id]\n' \
                  'rent - Rent a vehicle with [id]\n' \
                  'return - Return a vehicle [id] with [mileage]'

        self.assertEquals(self.machine.get_options(), options)

    def test_get_current_sale_info(self):
        coin_value = 10.0

        self.machine.add_vehicle(self.vehicle, 10)
        self.machine.start_sale(self.vehicle.id)
        self.machine.insert_coin(coin_value)

        current_sale_info = CurrentSaleInfo(coin_value, self.vehicle.price)
        res = self.machine.get_current_sale_info()

        self.assertEquals(res.paid, current_sale_info.paid)
        self.assertEquals(res.price, current_sale_info.price)

    def test_finish_sale_no_change(self):
        coin_value = 10.0

        self.machine.add_vehicle(self.vehicle, 10)
        self.machine.add_change(5.0, 1)
        self.machine.start_sale(self.vehicle.id)
        self.machine.insert_coin(coin_value)

        self.assertTrue(self.machine.finish_sale() == 0.0)

    def test_finish_sale(self):
        coin_value = 20.0

        self.machine.add_vehicle(self.vehicle, 10)
        self.machine.add_change(0.01, 10)
        self.machine.add_change(0.02, 10)
        self.machine.add_change(0.10, 10)
        self.machine.add_change(0.20, 10)
        self.machine.add_change(0.50, 10)
        self.machine.add_change(1.0, 10)
        self.machine.add_change(2.0, 10)
        self.machine.add_change(5.0, 10)
        self.machine.start_sale(self.vehicle.id)
        self.machine.insert_coin(coin_value)

        self.assertEquals(self.machine.finish_sale(), coin_value - self.vehicle.price)
        self.assertEquals(self.machine.stock[self.vehicle.id]['stock'], 9)
        self.assertEquals(self.machine.current_sale, None)
        self.assertEquals(self.machine.cashier.current_amount, 0.0)
