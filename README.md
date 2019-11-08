# PMat
A Python class that allows for tracking of units with numbers and disallows operations that are nonsense.

## Usage
A PMat class can be declared using the class `PMat(num,unit)` where `num` is a simple integer or float and `unit` is a string containing the unit to associate with the value. The class has support to act like a normal Python int in normal operation, but the class will check to ensure compatibility before each operation. The class will also update units when appropriately, like during multiplication. PMat will also work with int's regardless of unit and it is possible to create a PMat class without a unit (thus acting like a standard int).

### Todo
- Create PMat class
  - Use re's to parse input unit
    - Custom units will be decomposed on initial parse
    - After successful parse, compress units so every present unit appears only once
    - Custom units should be stored by their decomposition
      - Allows for printing to quickly identify if it should print as a custom unit instead of a SI conglomeration
  - Add int operation
    - Following operation creates completely new PMat object to prevent side effects
    - Add
    - Subtract
    - Multiplication
    - Division
    - Modulo
    - Floor
    - Ceiling
    - Should addition respect unit?
      - ie: 1km + 1 = 1.001km or 2km?
- Create function(s) that will convert prefix of a PMat object
  - Take string unit as input to specify preferred form of the PMat
