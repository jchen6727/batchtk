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
 
#define nrn_init _nrn_init__kacurrent
#define _nrn_initial _nrn_initial__kacurrent
#define nrn_cur _nrn_cur__kacurrent
#define _nrn_current _nrn_current__kacurrent
#define nrn_jacob _nrn_jacob__kacurrent
#define nrn_state _nrn_state__kacurrent
#define _net_receive _net_receive__kacurrent 
#define iassign iassign__kacurrent 
#define rates rates__kacurrent 
#define states states__kacurrent 
 
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
#define gd _p[1]
#define gd_columnindex 1
#define e _p[2]
#define e_columnindex 2
#define ika _p[3]
#define ika_columnindex 3
#define ikad _p[4]
#define ikad_columnindex 4
#define ninf _p[5]
#define ninf_columnindex 5
#define ntau _p[6]
#define ntau_columnindex 6
#define ndinf _p[7]
#define ndinf_columnindex 7
#define ndtau _p[8]
#define ndtau_columnindex 8
#define linf _p[9]
#define linf_columnindex 9
#define ltau _p[10]
#define ltau_columnindex 10
#define n _p[11]
#define n_columnindex 11
#define nd _p[12]
#define nd_columnindex 12
#define l _p[13]
#define l_columnindex 13
#define Dn _p[14]
#define Dn_columnindex 14
#define Dnd _p[15]
#define Dnd_columnindex 15
#define Dl _p[16]
#define Dl_columnindex 16
#define v _p[17]
#define v_columnindex 17
#define _g _p[18]
#define _g_columnindex 18
 
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
 "setdata_kacurrent", _hoc_setdata,
 "iassign_kacurrent", _hoc_iassign,
 "rates_kacurrent", _hoc_rates,
 0, 0
};
 /* declare global and static user variables */
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "g_kacurrent", "mho/cm2",
 "gd_kacurrent", "mho/cm2",
 "e_kacurrent", "mV",
 "ika_kacurrent", "mA/cm2",
 "ikad_kacurrent", "mA/cm2",
 "ntau_kacurrent", "ms",
 "ndtau_kacurrent", "ms",
 "ltau_kacurrent", "ms",
 0,0
};
 static double delta_t = 0.01;
 static double l0 = 0;
 static double nd0 = 0;
 static double n0 = 0;
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
"kacurrent",
 "g_kacurrent",
 "gd_kacurrent",
 "e_kacurrent",
 0,
 "ika_kacurrent",
 "ikad_kacurrent",
 "ninf_kacurrent",
 "ntau_kacurrent",
 "ndinf_kacurrent",
 "ndtau_kacurrent",
 "linf_kacurrent",
 "ltau_kacurrent",
 0,
 "n_kacurrent",
 "nd_kacurrent",
 "l_kacurrent",
 0,
 0};
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 19, _prop);
 	/*initialize range parameters*/
 	g = 0.048;
 	gd = 0;
 	e = -90;
 	_prop->param = _p;
 	_prop->param_size = 19;
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

 void _CA1ika_reg() {
	int _vectorized = 1;
  _initlists();
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 19, 1);
  hoc_register_dparam_semantics(_mechtype, 0, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 kacurrent /ddn/jchen/dev/pubtk/pubtk/examples/mod/CA1ika.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "Ika CA1";

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
   ika = g * n * l * ( v - e ) ;
   ikad = gd * nd * l * ( v - e ) ;
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
   Dn = ( ninf - n ) / ntau ;
   Dl = ( linf - l ) / ltau ;
   Dnd = ( ndinf - nd ) / ndtau ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) {
 rates ( _threadargscomma_ v ) ;
 Dn = Dn  / (1. - dt*( ( ( ( - 1.0 ) ) ) / ntau )) ;
 Dl = Dl  / (1. - dt*( ( ( ( - 1.0 ) ) ) / ltau )) ;
 Dnd = Dnd  / (1. - dt*( ( ( ( - 1.0 ) ) ) / ndtau )) ;
  return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) { {
   rates ( _threadargscomma_ v ) ;
    n = n + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / ntau)))*(- ( ( ( ninf ) ) / ntau ) / ( ( ( ( - 1.0 ) ) ) / ntau ) - n) ;
    l = l + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / ltau)))*(- ( ( ( linf ) ) / ltau ) / ( ( ( ( - 1.0 ) ) ) / ltau ) - l) ;
    nd = nd + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / ndtau)))*(- ( ( ( ndinf ) ) / ndtau ) / ( ( ( ( - 1.0 ) ) ) / ndtau ) - nd) ;
   }
  return 0;
}
 
static int  rates ( _threadargsprotocomma_ double _lv ) {
   double _la , _lb ;
  _la = exp ( - 0.038 * ( 1.5 + 1.0 / ( 1.0 + exp ( _lv + 40.0 ) / 5.0 ) ) * ( _lv - 11.0 ) ) ;
   _lb = exp ( - 0.038 * ( 0.825 + 1.0 / ( 1.0 + exp ( _lv + 40.0 ) / 5.0 ) ) * ( _lv - 11.0 ) ) ;
   ntau = 4.0 * _lb / ( 1.0 + _la ) ;
   if ( ntau < 0.1 ) {
     ntau = 0.1 ;
     }
   ninf = 1.0 / ( 1.0 + _la ) ;
   _la = exp ( - 0.038 * ( 1.8 + 1.0 / ( 1.0 + exp ( _lv + 40.0 ) / 5.0 ) ) * ( _lv + 1.0 ) ) ;
   _lb = exp ( - 0.038 * ( 0.7 + 1.0 / ( 1.0 + exp ( _lv + 40.0 ) / 5.0 ) ) * ( _lv + 1.0 ) ) ;
   ndtau = 2.0 * _lb / ( 1.0 + _la ) ;
   if ( ndtau < 0.1 ) {
     ndtau = 0.1 ;
     }
   ndinf = 1.0 / ( 1.0 + _la ) ;
   _la = exp ( 0.11 * ( _lv + 56.0 ) ) ;
   ltau = 0.26 * ( _lv + 50.0 ) ;
   if ( ltau < 2.0 ) {
     ltau = 2.0 ;
     }
   linf = 1.0 / ( 1.0 + _la ) ;
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
  l = l0;
  nd = nd0;
  n = n0;
 {
   rates ( _threadargscomma_ v ) ;
   n = ninf ;
   l = linf ;
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
 _current += ika;
 _current += ikad;

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
 _slist1[0] = n_columnindex;  _dlist1[0] = Dn_columnindex;
 _slist1[1] = l_columnindex;  _dlist1[1] = Dl_columnindex;
 _slist1[2] = nd_columnindex;  _dlist1[2] = Dnd_columnindex;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/ddn/jchen/dev/pubtk/pubtk/examples/mod/CA1ika.mod";
static const char* nmodl_file_text = 
  ": $Id: CA1ika.mod,v 1.2 2010/12/01 05:06:07 samn Exp $ \n"
  "TITLE Ika CA1\n"
  "\n"
  "UNITS {\n"
  "  (mA) = (milliamp)\n"
  "  (mV) = (millivolt)\n"
  "}\n"
  " \n"
  "NEURON {\n"
  "  SUFFIX kacurrent\n"
  "  NONSPECIFIC_CURRENT ika, ikad\n"
  "  RANGE g, gd, e, ninf, ntau, ndinf, ndtau, linf, ltau\n"
  "}\n"
  " \n"
  "PARAMETER {\n"
  "  celsius	(degC)\n"
  "  g= 0.048	(mho/cm2)\n"
  "  gd= 0		(mho/cm2)\n"
  "  e= -90	(mV)\n"
  "}\n"
  " \n"
  "STATE {\n"
  "  n\n"
  "  nd : distal\n"
  "  l\n"
  "}\n"
  " \n"
  "ASSIGNED {\n"
  "  v	(mV)\n"
  "  ika	(mA/cm2) \n"
  "  ikad	(mA/cm2)\n"
  "  ninf\n"
  "  ntau  (ms)\n"
  "  ndinf\n"
  "  ndtau (ms)\n"
  "  linf\n"
  "  ltau	(ms)\n"
  "}\n"
  "\n"
  "PROCEDURE iassign () {\n"
  "  ika=g*n*l*(v-e)\n"
  "  ikad=gd*nd*l*(v-e)\n"
  "}\n"
  " \n"
  "BREAKPOINT {\n"
  "  SOLVE states METHOD cnexp\n"
  "  iassign()\n"
  "}\n"
  " \n"
  "DERIVATIVE states { \n"
  "  rates(v)\n"
  "  n'= (ninf- n)/ ntau\n"
  "  l'= (linf- l)/ ltau\n"
  "  nd'= (ndinf-nd)/ndtau\n"
  "}\n"
  "\n"
  "INITIAL { \n"
  "  rates(v)\n"
  "  n = ninf\n"
  "  l = linf\n"
  "  iassign()\n"
  "}\n"
  "\n"
  "PROCEDURE rates(v (mV)) {\n"
  "  LOCAL  a, b\n"
  "  UNITSOFF\n"
  "  a = exp(-0.038*(1.5+1/(1+exp(v+40)/5))*(v-11))\n"
  "  b =	exp(-0.038*(0.825+1/(1+exp(v+40)/5))*(v-11))\n"
  "  ntau=4*b/(1+a)\n"
  "  if (ntau<0.1) {ntau=0.1}\n"
  "  ninf=1/(1+a)\n"
  "	\n"
  "  a=exp(-0.038*(1.8+1/(1+exp(v+40)/5))*(v+1))\n"
  "  b=exp(-0.038*(0.7+1/(1+exp(v+40)/5))*(v+1))\n"
  "  ndtau=2*b/(1+a)\n"
  "  if (ndtau<0.1) {ndtau=0.1}\n"
  "  ndinf=1/(1+a)\n"
  "\n"
  "  a = exp(0.11*(v+56))\n"
  "  ltau=0.26*(v+50)\n"
  "  if (ltau<2) {ltau=2}\n"
  "  linf=1/(1+a)\n"
  "  UNITSON\n"
  "}\n"
  "\n"
  ;
#endif
