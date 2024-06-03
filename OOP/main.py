from car import Car 


car_1 = Car("Chevy", "Corvette", 2021, "blue")
car_2 = Car("Chevy", "model1", 2024, "red")

car_1.wheels = 3
print(car_1.wheels)
print(car_2.wheels)

car_1.drive()
car_2.drive()
