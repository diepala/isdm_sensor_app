from math import log, exp

def _R(T, R25, A, B, C, D):
    '''Devuelve la resistencia en función de la temperatura'''
    return R25 * exp(A + B/T + C/(T**2) + D/(T**3))

def _T(R, R25, A, B, C, D):
    '''Devuelve la temperatura en función de la resistencia'''
    return 1.0 / (A + B * log(R / R25) + C * log(R / R25)**2 + D * log(R / R25)**3)
    
def R_S1(T):
    '''R en función de T para S1'''
    if T < (25 + 273.15):
        return _R(T, 2060.0, -12.00258172, 3670.667, -7617.13, -5914730.0)
    else:
        return _R(T, 2060.0, -21.01338172, 11886.95, -2504699.0, 247033800.0)
        
def R_S2(T):
    '''R en función de T para S2'''
    return _R(T, 2200.0, -14.63371957, 4791.842, -115334.0, -3730535.0)
    
def T_S1(R):
    '''T en función de R para S1'''
    res = _T(R, 2060.0, 0.003354016, 0.000292415, 1.65418e-6, 7.40746e-8)
    if res < (273.15 + 25):
        return res
    else:
        return _T(R, 2060.0, 0.003354005, 0.000294908, 3.58168e-6, -7.78607e-7)
        
def T_S2(R):
    '''T en función de R para S2'''
    return _T(R, 2200.0, 0.003354016, 0.000256985, 2.62013e-6, 6.38309e-8)