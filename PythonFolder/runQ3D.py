import matlab.engine
eng = matlab.engine.start_matlab()

#a = eng.workspace['a']
span = 14.5

[CLdes,CDdes] = eng.Q3Drunner(span, nargout=2)

eng.quit()

print(CLdes,CDdes)