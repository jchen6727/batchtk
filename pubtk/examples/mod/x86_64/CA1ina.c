/* Created by Language version: 7.7.0 */
/* VECTORIZED */
#define NRN_VECTORIZED 1
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "mech_api.h"
#undef PI
#define nil 0
#include "md1redef.h"
#include "section.h"
#include "nrniv_mf.h"
#include "md2redef.h"
 
#if METHOD3
extern int _method3;
#endif

#if !NRNGPU
#undef exp
#define exp hoc_Exp
extern double hoc_Exp(double);
#endif
 
#define nrn_init _nrn_init__nacurrent
#define _nrn_initial _nrn_initial__nacurrent
#define nrn_cur _nrn_cur__nacurrent
#define _nrn_current _nrn_current__nacurrent
#define nrn_jacob _nrn_jacob__nacurrent
#define nrn_state _nrn_state__nacurrent
#define _net_receive _net_receive__nacurrent 
#define iassign iassign__nacurrent 
#define rates rates__nacurrent 
#define states states__nacurrent 
 
#define _threadargscomma_ _p, _ppvar, _thread, _nt,
#define _threadargsprotocomma_ double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt,
#define _threadargs_ _p, _ppvar, _thread, _nt
#define _threadargsproto_ double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt
 	/*SUPPRESS 761*/
	/*SUPPRESS 762*/
	/*SUPPRESS 763*/
	/*SUPPRESS 765*/
	 extern double *getarg();
 /* Thread safe. No static _p or _ppvar. */
 
#define t _nt->_t
#define dt _nt->_dt
#define g _p[0]
#define g_columnindex 0
#define e _p[1]
#define e_columnindex 1
#define vi _p[2]
#define vi_columnindex 2
#define ki _p[3]
#define ki_columnindex 3
#define ina _p[4]
#define ina_columnindex 4
#define minf _p[5]
#define minf_columnindex 5
#define mtau _p[6]
#define mtau_columnindex 6
#define hinf _p[7]
#define hinf_columnindex 7
#define htau _p[8]
#define htau_columnindex 8
#define iinf _p[9]
#define iinf_columnindex 9
#define itau _p[10]
#define itau_columnindex 10
#define m _p[11]
#define m_columnindex 11
#define h _p[12]
#define h_columnindex 12
#define I _p[13]
#define I_columnindex 13
#define Dm _p[14]
#define Dm_columnindex 14
#define Dh _p[15]
#define Dh_columnindex 15
#define DI _p[16]
#define DI_columnindex 16
#define i _p[17]
#define i_columnindex 17
#define v _p[18]
#define v_columnindex 18
#define _g _p[19]
#define _g_columnindex 19
 
#if MAC
#if !defined(v)
#define v _mlhv
#endif
#if !defined(h)
#define h _mlhh
#endif
#endif
 
#if defined(__cplusplus)
extern "C" {
#endif
 static int hoc_nrnpointerindex =  -1;
 static Datum* _extcall_thread;
 static Prop* _extcall_prop;
 /* external NEURON variables */
 extern double celsius;
 /* declaration of user functions */
 static void _hoc_iassign(void);
 static void _hoc_rates(void);
 static int _mechtype;
extern void _nrn_cacheloop_reg(int, int);
extern void hoc_register_prop_size(int, int, int);
extern void hoc_register_limits(int, HocParmLimits*);
extern void hoc_register_units(int, HocParmUnits*);
extern void nrn_promote(Prop*, int, int);
extern Memb_func* memb_func;
 
#define NMODL_TEXT 1
#if NMODL_TEXT
static const char* nmodl_file_text;
static const char* nmodl_filename;
extern void hoc_reg_nmodl_text(int, const char*);
extern void hoc_reg_nmodl_filename(int, const char*);
#endif

 extern void _nrn_setdata_reg(int, void(*)(Prop*));
 static void _setdata(Prop* _prop) {
 _extcall_prop = _prop;
 }
 static void _hoc_setdata() {
 Prop *_prop, *hoc_getdata_range(int);
 _prop = hoc_getdata_range(_mechtype);
   _setdata(_prop);
 hoc_retpushx(1.);
}
 /* connect user functions to hoc names */
 static VoidFunc hoc_intfunc[] = {
 "setdata_nacurrent", _hoc_setdata,
 "iassign_nacurrent", _hoc_iassign,
 "rates_nacurrent", _hoc_rates,
 0, 0
};
 /* declare global and static user variables */
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "g_nacurrent", "mho/cm2",
 "e_nacurrent", "mV",
 "vi_nacurrent", "mV",
 "ina_nacurrent", "mA/cm2",
 "mtau_nacurrent", "ms",
 "htau_nacurrent", "ms",
 "itau_nacurrent", "ms",
 0,0
};
 static double I0 = 0;
 static double delta_t = 0.01;
 static double h0 = 0;
 static double m0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 0,0
};
 static DoubVec hoc_vdoub[] = {
 0,0,0
};
 static double _sav_indep;
 static void nrn_alloc(Prop*);
static void  nrn_init(NrnThread*, _Memb_list*, int);
static void nrn_state(NrnThread*, _Memb_list*, int);
 static void nrn_cur(NrnThread*, _Memb_list*, int);
static void  nrn_jacob(NrnThread*, _Memb_list*, int);
 
static int _ode_count(int);
static void _ode_map(int, double**, double**, double*, Datum*, double*, int);
static void _ode_spec(NrnThread*, _Memb_list*, int);
static void _ode_matsol(NrnThread*, _Memb_list*, int);
 
#define _cvode_ieq _ppvar[0]._i
 static void _ode_matsol_instance1(_threadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"nacurrent",
 "g_nacurrent",
 "e_nacurrent",
 "vi_nacurrent",
 "ki_nacurrent",
 0,
 "ina_nacurrent",
 "minf_nacurrent",
 "mtau_nacurrent",
 "hinf_nacurrent",
 "htau_nacurrent",
 "iinf_nacurrent",
 "itau_nacurrent",
 0,
 "m_nacurrent",
 "h_nacurrent",
 "I_nacurrent",
 0,
 0};
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 20, _prop);
 	/*initialize range parameters*/
 	g = 0.032;
 	e = 55;
 	vi = -60;
 	ki = 0.8;
 	_prop->param = _p;
 	_prop->param_size = 20;
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 1, _prop);
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 0,0
};
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _CA1ina_reg() {
	int _vectorized = 1;
  _initlists();
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 20, 1);
  hoc_register_dparam_semantics(_mechtype, 0, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 nacurrent /ddn/jchen/dev/optimization/CA3/mod/CA1ina.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "INa CA1";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int iassign(_threadargsproto_);
static int rates(_threadargsprotocomma_ double);
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[3], _dlist1[3];
 static int states(_threadargsproto_);
 
static int  iassign ( _threadargsproto_ ) {
   i = g * m * m * m * h * I * ( v - e ) ;
   ina = i ;
    return 0; }
 
static void _hoc_iassign(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r = 1.;
 iassign ( _p, _ppvar, _thread, _nt );
 hoc_retpushx(_r);
}
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) {int _reset = 0; {
   rates ( _threadargscomma_ v ) ;
   Dm = ( minf - m ) / mtau ;
   Dh = ( hinf - h ) / htau ;
   DI = ( iinf - I ) / itau ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) {
 rates ( _threadargscomma_ v ) ;
 Dm = Dm  / (1. - dt*( ( ( ( - 1.0 ) ) ) / mtau )) ;
 Dh = Dh  / (1. - dt*( ( ( ( - 1.0 ) ) ) / htau )) ;
 DI = DI  / (1. - dt*( ( ( ( - 1.0 ) ) ) / itau )) ;
  return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) { {
   rates ( _threadargscomma_ v ) ;
    m = m + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / mtau)))*(- ( ( ( minf ) ) / mtau ) / ( ( ( ( - 1.0 ) ) ) / mtau ) - m) ;
    h = h + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / htau)))*(- ( ( ( hinf ) ) / htau ) / ( ( ( ( - 1.0 ) ) ) / htau ) - h) ;
    I = I + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / itau)))*(- ( ( ( iinf ) ) / itau ) / ( ( ( ( - 1.0 ) ) ) / itau ) - I) ;
   }
  return 0;
}
 
static int  rates ( _threadargsprotocomma_ double _lv ) {
   double _la , _lb ;
  _la = 0.4 * ( _lv + 30.0 ) / ( 1.0 - exp ( - ( _lv + 30.0 ) / 7.2 ) ) ;
   _lb = 0.124 * ( _lv + 30.0 ) / ( exp ( ( _lv + 30.0 ) / 7.2 ) - 1.0 ) ;
   mtau = 0.5 / ( _la + _lb ) ;
   if ( mtau < 0.02 ) {
     mtau = 0.02 ;
     }
   minf = _la / ( _la + _lb ) ;
   _la = 0.03 * ( _lv + 45.0 ) / ( 1.0 - exp ( - ( _lv + 45.0 ) / 1.5 ) ) ;
   _lb = 0.01 * ( _lv + 45.0 ) / ( exp ( ( _lv + 45.0 ) / 1.5 ) - 1.0 ) ;
   htau = 0.5 / ( _la + _lb ) ;
   if ( htau < 0.5 ) {
     htau = 0.5 ;
     }
   hinf = 1.0 / ( 1.0 + exp ( ( _lv + 50.0 ) / 4.0 ) ) ;
   _la = exp ( 0.45 * ( _lv + 66.0 ) ) ;
   _lb = exp ( 0.09 * ( _lv + 66.0 ) ) ;
   itau = 3000.0 * _lb / ( 1.0 + _la ) ;
   if ( itau < 10.0 ) {
     itau = 10.0 ;
     }
   iinf = ( 1.0 + ki * exp ( ( _lv - vi ) / 2.0 ) ) / ( 1.0 + exp ( ( _lv - vi ) / 2.0 ) ) ;
     return 0; }
 
static void _hoc_rates(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r = 1.;
 rates ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
static int _ode_count(int _type){ return 3;}
 
static void _ode_spec(NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
     _ode_spec1 (_p, _ppvar, _thread, _nt);
 }}
 
static void _ode_map(int _ieq, double** _pv, double** _pvdot, double* _pp, Datum* _ppd, double* _atol, int _type) { 
	double* _p; Datum* _ppvar;
 	int _i; _p = _pp; _ppvar = _ppd;
	_cvode_ieq = _ieq;
	for (_i=0; _i < 3; ++_i) {
		_pv[_i] = _pp + _slist1[_i];  _pvdot[_i] = _pp + _dlist1[_i];
		_cvode_abstol(_atollist, _atol, _i);
	}
 }
 
static void _ode_matsol_instance1(_threadargsproto_) {
 _ode_matsol1 (_p, _ppvar, _thread, _nt);
 }
 
static void _ode_matsol(NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
 _ode_matsol_instance1(_threadargs_);
 }}

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) {
  int _i; double _save;{
  I = I0;
  h = h0;
  m = m0;
 {
   rates ( _threadargscomma_ v ) ;
   h = hinf ;
   m = minf ;
   I = iinf ;
   iassign ( _threadargs_ ) ;
   }
 
}
}

static void nrn_init(NrnThread* _nt, _Memb_list* _ml, int _type){
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 v = _v;
 initmodel(_p, _ppvar, _thread, _nt);
}
}

static double _nrn_current(double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt, double _v){double _current=0.;v=_v;{ {
   iassign ( _threadargs_ ) ;
   }
 _current += ina;

} return _current;
}

static void nrn_cur(NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; double _rhs, _v; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 _g = _nrn_current(_p, _ppvar, _thread, _nt, _v + .001);
 	{ _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
 	}
 _g = (_g - _rhs)/.001;
#if CACHEVEC
  if (use_cachevec) {
	VEC_RHS(_ni[_iml]) -= _rhs;
  }else
#endif
  {
	NODERHS(_nd) -= _rhs;
  }
 
}
 
}

static void nrn_jacob(NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml];
#if CACHEVEC
  if (use_cachevec) {
	VEC_D(_ni[_iml]) += _g;
  }else
#endif
  {
     _nd = _ml->_nodelist[_iml];
	NODED(_nd) += _g;
  }
 
}
 
}

static void nrn_state(NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v = 0.0; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
 _nd = _ml->_nodelist[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 v=_v;
{
 {   states(_p, _ppvar, _thread, _nt);
  }}}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = m_columnindex;  _dlist1[0] = Dm_columnindex;
 _slist1[1] = h_columnindex;  _dlist1[1] = Dh_columnindex;
 _slist1[2] = I_columnindex;  _dlist1[2] = DI_columnindex;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/ddn/jchen/dev/optimization/CA3/mod/CA1ina.mod";
static const char* nmodl_file_text = 
  ": $Id: CA1ina.mod,v 1.4 2010/11/30 19:50:00 samn Exp $ \n"
  "TITLE INa CA1\n"
  "\n"
  "UNITS {\n"
  "  (mA) = (milliamp)\n"
  "  (mV) = (millivolt)\n"
  "}\n"
  "\n"
  "NEURON {\n"
  "  SUFFIX nacurrent\n"
  "  NONSPECIFIC_CURRENT ina\n"
  "  RANGE g, e, vi, ki\n"
  "  RANGE minf,hinf,iinf,mtau,htau,itau : testing\n"
  "}\n"
  "  \n"
  "PARAMETER {\n"
  "  : v	    (mV)\n"
  "  celsius	    (degC)\n"
  "  g = 0.032   (mho/cm2)\n"
  "  e = 55	    (mV)\n"
  "  vi = -60    (mV)\n"
  "  ki = 0.8\n"
  "}\n"
  " \n"
  "STATE {\n"
  "  m\n"
  "  h\n"
  "  I : i \n"
  "}\n"
  " \n"
  "ASSIGNED {\n"
  "  i (mA/cm2)\n"
  "  ina	(mA/cm2) \n"
  "  minf\n"
  "  mtau    (ms)\n"
  "  hinf\n"
  "  htau	(ms)\n"
  "  iinf\n"
  "  itau	(ms)\n"
  "  v	(mV) : testing\n"
  "}\n"
  "\n"
  ": PROCEDURE iassign () { ina=g*m*m*m*h*i*(v-e) }\n"
  "PROCEDURE iassign () { i=g*m*m*m*h*I*(v-e) ina=i}\n"
  " \n"
  "BREAKPOINT {\n"
  "  SOLVE states METHOD cnexp\n"
  "  iassign()\n"
  "}\n"
  " \n"
  "DERIVATIVE states { \n"
  "  rates(v)\n"
  "  m' = (minf - m) / mtau\n"
  "  h' = (hinf - h) / htau\n"
  "  : i' = (iinf - i) / itau	    \n"
  "  I' = (iinf - I) / itau	    \n"
  "}\n"
  "\n"
  "INITIAL { \n"
  "  rates(v)\n"
  "  h = hinf\n"
  "  m = minf\n"
  "  : i = iinf\n"
  "  I = iinf\n"
  "  iassign() : testing\n"
  "}\n"
  "\n"
  "\n"
  "PROCEDURE rates(v (mV)) {\n"
  "  LOCAL  a, b\n"
  "  UNITSOFF\n"
  "  a = 0.4*(v+30)/(1-exp(-(v+30)/7.2))\n"
  "  b = 0.124*(v+30)/(exp((v+30)/7.2)-1) 	\n"
  "  mtau=0.5/(a+b)\n"
  "  if (mtau<0.02) {mtau=0.02}\n"
  "  minf=a/(a+b)\n"
  "  a = 0.03*(v+45)/(1-exp(-(v+45)/1.5))\n"
  "  b = 0.01*(v+45)/(exp((v+45)/1.5)-1)\n"
  "  htau=0.5/(a+b)\n"
  "  if (htau<0.5) {htau=0.5}\n"
  "  hinf=1/(1+exp((v+50)/4))\n"
  "  a =	exp(0.45*(v+66))\n"
  "  b = exp(0.09*(v+66))\n"
  "  itau=3000*b/(1+a)\n"
  "  if (itau<10) {itau=10}\n"
  "  iinf=(1+ki*exp((v-vi)/2))/(1+exp((v-vi)/2))\n"
  "  UNITSON\n"
  "}\n"
  "\n"
  ;
#endif
