numOfFrame= Get number of frames
writeFileLine: "a.csv","0.0,0.0"
string$=""
mean1=0
for step to numOfFrame
    tmin = Get time from frame number: step
    tmax = Get time from frame number: step+1
    mean = Get mean: tmin, tmax, "Hertz"
    minimum = Get minimum: tmin, tmax, "Hertz", "Parabolic"
    maximum = Get maximum: tmin, tmax, "Hertz", "Parabolic"
    stdev = Get standard deviation: tmin, tmax, "Hertz"
    tmean$=string$(tmin+tmax/2)
    mean$=string$(mean)
    if mean!=undefined
        mean$=string$(mean)
    else
        mean$=string$(4401)       
    endif
    string$= string$+newline$+tmean$+","+mean$
endfor
appendFileLine: "a.csv", string$