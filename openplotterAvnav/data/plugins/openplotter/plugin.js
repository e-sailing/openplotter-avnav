const formatRevolutions=function(data,opt_unit){
    try{
        if (opt_unit == 'Hz'){
            return avnav.api.formatter.formatDecimal(data,3,1);
        }
        else{
            return avnav.api.formatter.formatDecimal(60.0*parseFloat(data),4,0)
        }
    }catch(e){
        return "-----"
    }
}
formatRevolutions.parameters=[
    {name:'unit',type:'SELECT',list:['RPM','Hz'],default:'RPM'}
]
avnav.api.registerFormatter("sk_Hz",formatRevolutions);

// m3
const format_m3=function(data,opt_unit){
    try{
        if (opt_unit == 'm3'){
            return avnav.api.formatter.formatDecimal(data,2,3);
        }
        else if (opt_unit == 'l'){
            return avnav.api.formatter.formatDecimal(1000.0*parseFloat(data),4,0)
        }
        else if (opt_unit == 'gal'){
            return avnav.api.formatter.formatDecimal(264,172*parseFloat(data),4,0)
        }
    }catch(e){
        return "-----"
    }
}
format_m3.parameters=[
    {name:'unit',type:'SELECT',list:['m3','l','gal'],default:'l'}
]
avnav.api.registerFormatter("sk_m3",format_m3);

// m
const format_m=function(data,opt_unit){
    try{
        if (opt_unit == 'm'){
            return avnav.api.formatter.formatDecimal(data,4,1);
        }
        else if (opt_unit == 'dm'){
            return avnav.api.formatter.formatDecimal(10.0*parseFloat(data),4,1)
        }
        else if (opt_unit == 'cm'){
            return avnav.api.formatter.formatDecimal(100.0*parseFloat(data),4,1)
        }
        else if (opt_unit == 'mm'){
            return avnav.api.formatter.formatDecimal(1000.0*parseFloat(data),4,1)
        }
        else if (opt_unit == 'nm'){
            return avnav.api.formatter.formatDecimal(0.000539957*parseFloat(data),4,1)
        }
        else if (opt_unit == 'km'){
            return avnav.api.formatter.formatDecimal(0.001*parseFloat(data),4,1)
        }
        else if (opt_unit == 'ft'){
            return avnav.api.formatter.formatDecimal(3.28084*parseFloat(data),4,1)
        }
    }catch(e){
        return "-----"
    }
}
format_m.parameters=[
    {name:'unit',type:'SELECT',list:['m','dm','cm','mm','nm','km','ft'],default:'nm'}
]
avnav.api.registerFormatter("sk_m",format_m);

// m/s
const format_m_s=function(data,opt_unit){
    try{
        if (opt_unit == 'm/s'){
            return avnav.api.formatter.formatDecimal(data,2,1);
        }
        else if (opt_unit == 'kn'){
            return avnav.api.formatter.formatDecimal(1.94384*parseFloat(data),2,1)
        }
        else if (opt_unit == 'kmh'){
            return avnav.api.formatter.formatDecimal(3.6*parseFloat(data),3,1)
        }
    }catch(e){
        return "-----"
    }
}
format_m_s.parameters=[
    {name:'unit',type:'SELECT',list:['m/s','kn','kmh'],default:'kn'}
]
avnav.api.registerFormatter("sk_m_s",format_m_s);

// %
const format_ratio=function(data,opt_unit){
    try{
        if (opt_unit == '%'){
            return avnav.api.formatter.formatDecimal(data,3,0);
        }
    }catch(e){
        return "-----"
    }
}
format_ratio.parameters=[
    {name:'unit',type:'SELECT',list:['%'],default:'%'}
]
avnav.api.registerFormatter("sk_ratio",format_ratio);

// °
const format_radiant=function(data,opt_unit){
    try{
        if (opt_unit == 'rad'){
            return avnav.api.formatter.formatDecimal(data,1,3);
        }
        else if (opt_unit == '°'){
            return avnav.api.formatter.formatDecimal(57.2958*parseFloat(data),3,0)
        }
    }catch(e){
        return "-----"
    }
}
format_radiant.parameters=[
    {name:'unit',type:'SELECT',list:['rad','°'],default:'°'}
]
avnav.api.registerFormatter("sk_degree",format_radiant);
