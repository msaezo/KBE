import matlab.engine
eng = matlab.engine.start_matlab()
eng.Q3Drunner(nargout=0)

#a = eng.workspace['a']

eng.quit()

#print(a)