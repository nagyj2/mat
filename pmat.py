#!/usr/local/bin/python3
import re
from math import log

class PMat:
    
    # Possible prefixes to use in units. In a form for use within re's
    _prefix = ["E","P","T","G","M","k","h","da","d(?!a)","c","m(?!($|ol))","u","n","p","f","a"]
    # All basic SI units to use in a PMat in re-compatible form
    _unit = ["mol","m(?!ol)","g","s","K","A","cd"]
    # re to detect the presence of an exponent within a unit
    _exponent = "([\^]?\d+)"
    
    _lookup_u = {
        "m"     : 0, "g"     : 1,
        "s"     : 2, "K"     : 3,
        "mol"   : 4, "A"     : 5,
        "cd"    : 6, "/"     : -1
    } # To look up index in _e and _p
    
    _lookup_p = {
        "E" : 18, "P" : 15,
        "T" : 12, "G" :  9,
        "M" :  6, "k" :  3,
        "h" :  2, "da":  1,
        ""  :  0, "d" : -1,
        "c" : -2, "m" : -3,
        "u" : -6, "n" : -9,
        "p" :-12, "f" :-15,
        "a" :-18
    } # To correlate a prefix with a number (10 ^ <prefix #>)
    
    _customunit = [] # Available custom units
    _custommean = {} # Dictionary relating custom units to their SI counterpart
    
    def __init__(self,num_or_pmat=0,unit=""):
        # PMat numerical variable (not factoring in prefix)
        self._n = 0
        # Prefix numerical representation
        self._p = [0,0,0,0,0,0,0] # m,g,s,K,mol,A,cd
        # Exponent of PMat number. A exponent of zero is equivalent of the unit not being present
        self._e = [0,0,0,0,0,0,0]
        
        if (type(num_or_pmat) == PMat):
            # Given another PMat as input; simply copy it
            self._n = num_or_pmat._n
            self._p = num_or_pmat._p
            self._e = num_or_pmat._e
        else:
            # Given number and unit separately
            self._n = num_or_pmat
            representation = PMat._decomposeUnit(unit)
            
            for si_unit in representation:
                prefix = si_unit[0]
                index = si_unit[1]
                exponent = si_unit[2]
                
                self._p[index] += prefix * exponent
                self._e[index] += exponent
        
    def __str__(self):
        return str(self._n) +'\n'+ str(self._p) +'\n'+ str(self._e)
            
    def isSame(self,other):
        # Returns whether the self and other PMat are of the same type
        for i in range(len(self._e)):
            if (self._e[i] != other._e[i]):
                return False
        return True
        
    def isUnitless(self):
        # Returns whether this PMat is unitless
        for iu in self._e:
            if (iu!=0): return False
        return True
            
    @staticmethod
    def _re_un():
        return str("|".join(PMat._unit))
        
    @staticmethod
    def _re_pf():
        return str("|".join(PMat._prefix))
    
    @staticmethod
    def _re_cu():
        # Returns a re compatible version of custom units
        if (len(PMat._customunit) == 0):
            return ""
            
        PMat._customunit.sort()
        return "|".join(PMat._customunit)
            
    @staticmethod
    def define(short,long):
        # If the custom unit doesnt exist, add it
        if (not short in PMat._customunit):
            PMat._customunit.append(short)
        # Either redefine unit or establish it
        PMat._custommean[short] = long
            
    @staticmethod
    def undefine(short_or_all=False):
        # If True, erase all custom units
        if (short_or_all == True):
            PMat._customunit = []
            PMat._custommean = {}
            return
            
        # Otherwise, remove a single custom unit
        for cunit in PMat._customunit:
            if (short_or_all == cunit):
                del PMat._custommean[short_or_all]
                PMat._customunit.remove(cunit)
                return
            
    @staticmethod
    def _decomposeUnit(string,top=1):
        # Returns an array where each element represents a sub unit containing:
        #   1st: Prefix (number)
        #   2nd: Base SI Unit (number) -> rep index of where on _e
        #   3rd: Exponent of unit (number)
        
        # Check if custom units are defined
        if (len(PMat._re_cu())>0):
            cu_expr = "|" + PMat._re_cu()
        else:
            cu_expr = ""
            
        expr_prefix_exist = "^(" + PMat._re_pf() + ")(" + PMat._re_un() + cu_expr + ")"
        expr_prefix_find = "^(" + PMat._re_pf() + ")"
        
        expr_unit_exist = "((" + PMat._re_un() + cu_expr + ")|/)"
        
        expr_exponent_exist = "([\^]?\d+)"
        
        expr_mult = re.compile("^\*")
        
        re_prefix_exist = re.compile(expr_prefix_exist)
        re_prefix_find = re.compile(expr_prefix_find)
        re_unit_exist = re.compile(expr_unit_exist)
        re_exponent_exist = re.compile(expr_exponent_exist)
        re_mult = re.compile(expr_mult)
        
        vector = []
        pos = 0
        while (pos < len(string)):
            prefix = ""
            unit = None
            exponent = 1 * top
            subunit = False # If the found unit is a custom unit
            
            # Skip on '*' found; Allows for pseudo-precidence
            m_mult = re_mult.match(string[pos:])
            if (m_mult):
                pos += m_mult.end()
                continue
                
            # First, check for existence of prefix
            m_prefix_exist = re_prefix_exist.match(string[pos:])
            if (m_prefix_exist):
                # If exists, match just the prefix
                m_prefix_find = re_prefix_find.match(string[pos:])
                prefix = string[pos:][m_prefix_find.start():m_prefix_find.end()]
                pos += m_prefix_find.end()
                
            m_unit_exist = re_unit_exist.match(string[pos:])
            if (m_unit_exist):
                # Ensure a unit exists and then take it
                unit = string[pos:][m_unit_exist.start():m_unit_exist.end()]
                pos += m_unit_exist.end()
                # If a divisor is found, flip the multiplier
                if (unit == "/"):
                    top *= -1
                    continue
                # If the unit is a custom unit, mark it
                elif (unit in PMat._customunit):
                    subunit = True
            else:
                raise Exception("No unit found:",string[pos:])
                
            m_exponent_exist = re_exponent_exist.match(string[pos:])
            if (m_exponent_exist):
                # If an exponent exists, take it
                exponent = string[pos:][m_exponent_exist.start():m_exponent_exist.end()]
                pos += m_exponent_exist.end()
                # According to grammar, exponent can have '^' in front, so remove it if it exists
                if (exponent[0] == "^"):    exponent = int(exponent[1:]) * top
                else:                       exponent = int(exponent) * top
                
            # If a subunit is found, append its pieces instead of
            if (subunit):
                si_unit_equiv = PMat._custommean[unit]
                unit = PMat._decomposeUnit(si_unit_equiv,top)
                
            # If unit is a list, it was a decomposed custom unit; Append all elements
            if (type(unit) == list):
                for subunit in unit:
                    # If the custom unit was raised to a power, raise the subunit's power
                    subunit[2] *= exponent
                    vector.append(subunit)
            # Append only SI units
            else:
                vector.append([PMat._lookup_p[prefix],PMat._lookup_u[unit],exponent])
                
        # Compress similar units to reduce number of si unit 'pieces'
        # vector = PMat._compressVector(vector)
        # Sort so that order doesnt matter
        vector.sort()
        return vector
    
    @staticmethod
    def _compressVector(vector):
        subvector = []
        
        i= 0
        while (i < len(vector)):
            # Initial values to check
            ip, iu, ie = vector[i][0], vector[i][1], vector[i][2]
            # New values to append to subvector - start with original
            np, nu, ne = ip, iu, ie
            # Start looking at next unit
            j = i + 1
            while (j < len(vector)):
                jp, ju, je = vector[j][0], vector[j][1], vector[j][2]
                if (iu == ju and ie == je):
                    np = log(10 ** np + 10 ** jp,10)
                    ne += je
                    del vector[j]
                else:
                    j += 1
            subvector.append([np,nu,ne])
            i += 1
        
        return subvector
                

if __name__ == '__main__':
    def test_PMat():
        PMat.define("Hz","/s")
        PMat.define("rad","m/m")
        PMat.define("sr","m2/m2")
        PMat.define("N","kgm/s2")
        PMat.define("Pa","N/m2")
        PMat.define("J","Nm")
        PMat.define("W","J/s")
        PMat.define("C","sA")
        PMat.define("V","W/A")
        PMat.define("F","C/V")
        PMat.define("O","V/A")
        PMat.define("S","/O")
        PMat.define("Wb","J/A")
        PMat.define("dC","K")
        PMat.define("lm","cd/sr")
        PMat.define("lx","cd/srm2")
        PMat.define("Gy","J/kg")
        PMat.define("kat","mol/s")
        PMat.define("T","Vs/m^2")
        PMat.define("H","Vs/A")
        PMat.define("S","s^3A^2/kgm^2")
        PMat.define("hr","s")
        PMat.define("L","dm^3")
        PMat.define("eV","C")
        PMat.define("bar","kPa")
        
        
        PMat(0,"kmkm").debug
        # PMat(PMat(5,"V")).debug
        # PMat(0,"mL").debug
        # PMat(0,"mm").debug
        # PMat(0,"mm").debug
        
    test_PMat()
