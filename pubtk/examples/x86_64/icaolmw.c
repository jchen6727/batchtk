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
 
#define nrn_init _nrn_init__ICaolmw
#define _nrn_initial _nrn_initial__ICaolmw
#define nrn_cur _nrn_cur__ICaolmw
#define _nrn_current _nrn_current__ICaolmw
#define nrn_jacob _nrn_jacob__ICaolmw
#define nrn_state _nrn_state__ICaolmw
#define _net_receive _net_receive__ICaolmw 
#define iassign iassign__ICaolmw 
 
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
#define gca _p[0]
#define gca_columnindex 0
#define eca _p[1]
#define eca_columnindex 1
#define ica _p[2]
#define ica_columnindex 2
#define v _p[3]
#define v_columnindex 3
#define _g _p[4]
#define _g_columnindex 4
#define _ion_ica	*_ppvar[0]._pval
#define _ion_dicadv	*_ppvar[1]._pval
 
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
 /* declaration of user functions */
 static void _hoc_fun3(void);
 static void _hoc_fun1(void);
 static void _hoc_fun2(void);
 static void _hoc_iassign(void);
 static void _hoc_max(void);
 static void _hoc_min(void);
 static void _hoc_mcainf(void);
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
 "setdata_ICaolmw", _hoc_setdata,
 "fun3_ICaolmw", _hoc_fun3,
 "fun1_ICaolmw", _hoc_fun1,
 "fun2_ICaolmw", _hoc_fun2,
 "iassign_ICaolmw", _hoc_iassign,
 "max_ICaolmw", _hoc_max,
 "min_ICaolmw", _hoc_min,
 "mcainf_ICaolmw", _hoc_mcainf,
 0, 0
};
#define fun3 fun3_ICaolmw
#define fun1 fun1_ICaolmw
#define fun2 fun2_ICaolmw
#define max max_ICaolmw
#define min min_ICaolmw
#define mcainf mcainf_ICaolmw
 extern double fun3( _threadargsprotocomma_ double , double , double , double );
 extern double fun1( _threadargsprotocomma_ double , double , double , double );
 extern double fun2( _threadargsprotocomma_ double , double , double , double );
 extern double max( _threadargsprotocomma_ double , double );
 extern double min( _threadargsprotocomma_ double , double );
 extern double mcainf( _threadargsprotocomma_ double );
 /* declare global and static user variables */
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "gca_ICaolmw", "mS/cm2",
 "eca_ICaolmw", "mV",
 0,0
};
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
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"ICaolmw",
 "gca_ICaolmw",
 "eca_ICaolmw",
 0,
 0,
 0,
 0};
 static Symbol* _ca_sym;
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
 	_p = nrn_prop_data_alloc(_mechtype, 5, _prop);
 	/*initialize range parameters*/
 	gca = 1;
 	eca = 120;
 	_prop->param = _p;
 	_prop->param_size = 5;
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 2, _prop);
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_ca_sym);
 	_ppvar[0]._pval = &prop_ion->param[3]; /* ica */
 	_ppvar[1]._pval = &prop_ion->param[4]; /* _ion_dicadv */
 
}
 static void _initlists();
 static void _update_ion_pointer(Datum*);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _icaolmw_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("ca", -10000.);
 	_ca_sym = hoc_lookup("ca_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 2, _update_ion_pointer);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 5, 2);
  hoc_register_dparam_semantics(_mechtype, 0, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "ca_ion");
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 ICaolmw /ddn/jchen/dev/pubtk/pubtk/examples/mod/icaolmw.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int iassign(_threadargsproto_);
 
static int  iassign ( _threadargsproto_ ) {
   ica = ( 1e-3 ) * gca * pow( mcainf ( _threadargscomma_ v ) , 2.0 ) * ( v - eca ) ;
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
 
double mcainf ( _threadargsprotocomma_ double _lv ) {
   double _lmcainf;
 _lmcainf = fun2 ( _threadargscomma_ _lv , - 20.0 , 1.0 , - 9.0 ) * 1.0 ;
   
return _lmcainf;
 }
 
static void _hoc_mcainf(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  mcainf ( _p, _ppvar, _thread, _nt, *getarg(1) );
 hoc_retpushx(_r);
}
 
double fun1 ( _threadargsprotocomma_ double _lv , double _lV0 , double _lA , double _lB ) {
   double _lfun1;
 _lfun1 = _lA * exp ( ( _lv - _lV0 ) / _lB ) ;
   
return _lfun1;
 }
 
static void _hoc_fun1(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  fun1 ( _p, _ppvar, _thread, _nt, *getarg(1) , *getarg(2) , *getarg(3) , *getarg(4) );
 hoc_retpushx(_r);
}
 
double fun2 ( _threadargsprotocomma_ double _lv , double _lV0 , double _lA , double _lB ) {
   double _lfun2;
 _lfun2 = _lA / ( exp ( ( _lv - _lV0 ) / _lB ) + 1.0 ) ;
   
return _lfun2;
 }
 
static void _hoc_fun2(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  fun2 ( _p, _ppvar, _thread, _nt, *getarg(1) , *getarg(2) , *getarg(3) , *getarg(4) );
 hoc_retpushx(_r);
}
 
double fun3 ( _threadargsprotocomma_ double _lv , double _lV0 , double _lA , double _lB ) {
   double _lfun3;
 if ( fabs ( ( _lv - _lV0 ) / _lB ) < 1e-6 ) {
     _lfun3 = _lA * _lB / 1.0 * ( 1.0 - 0.5 * ( _lv - _lV0 ) / _lB ) ;
     }
   else {
     _lfun3 = _lA / 1.0 * ( _lv - _lV0 ) / ( exp ( ( _lv - _lV0 ) / _lB ) - 1.0 ) ;
     }
   
return _lfun3;
 }
 
static void _hoc_fun3(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  fun3 ( _p, _ppvar, _thread, _nt, *getarg(1) , *getarg(2) , *getarg(3) , *getarg(4) );
 hoc_retpushx(_r);
}
 
double min ( _threadargsprotocomma_ double _lx , double _ly ) {
   double _lmin;
 if ( _lx <= _ly ) {
     _lmin = _lx ;
     }
   else {
     _lmin = _ly ;
     }
   
return _lmin;
 }
 
static void _hoc_min(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  min ( _p, _ppvar, _thread, _nt, *getarg(1) , *getarg(2) );
 hoc_retpushx(_r);
}
 
double max ( _threadargsprotocomma_ double _lx , double _ly ) {
   double _lmax;
 if ( _lx >= _ly ) {
     _lmax = _lx ;
     }
   else {
     _lmax = _ly ;
     }
   
return _lmax;
 }
 
static void _hoc_max(void) {
  double _r;
   double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   if (_extcall_prop) {_p = _extcall_prop->param; _ppvar = _extcall_prop->dparam;}else{ _p = (double*)0; _ppvar = (Datum*)0; }
  _thread = _extcall_thread;
  _nt = nrn_threads;
 _r =  max ( _p, _ppvar, _thread, _nt, *getarg(1) , *getarg(2) );
 hoc_retpushx(_r);
}
 extern void nrn_update_ion_pointer(Symbol*, Datum*, int, int);
 static void _update_ion_pointer(Datum* _ppvar) {
   nrn_update_ion_pointer(_ca_sym, _ppvar, 0, 3);
   nrn_update_ion_pointer(_ca_sym, _ppvar, 1, 4);
 }

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) {
  int _i; double _save;{
 {
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
 _current += ica;

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
 	{ double _dica;
  _dica = ica;
 _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
  _ion_dicadv += (_dica - ica)/.001 ;
 	}
 _g = (_g - _rhs)/.001;
  _ion_ica += ica ;
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

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/ddn/jchen/dev/pubtk/pubtk/examples/mod/icaolmw.mod";
static const char* nmodl_file_text = 
  ": $Id: icaolmw.mod,v 1.2 2010/11/30 16:44:13 samn Exp $ \n"
  "COMMENT\n"
  "\n"
  "//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
  "//\n"
  "// NOTICE OF COPYRIGHT AND OWNERSHIP OF SOFTWARE\n"
  "//\n"
  "// Copyright 2007, The University Of Pennsylvania\n"
  "// 	School of Engineering & Applied Science.\n"
  "//   All rights reserved.\n"
  "//   For research use only; commercial use prohibited.\n"
  "//   Distribution without permission of Maciej T. Lazarewicz not permitted.\n"
  "//   mlazarew@seas.upenn.edu\n"
  "//\n"
  "//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
  "\n"
  "ENDCOMMENT\n"
  "\n"
  "UNITS {\n"
  "  (mA) = (milliamp)\n"
  "  (mV) = (millivolt)\n"
  "  (mS) = (millisiemens)\n"
  "}\n"
  "\n"
  "NEURON {\n"
  "  SUFFIX ICaolmw\n"
  "  USEION ca WRITE ica\n"
  "  RANGE gca,eca\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "  gca = 1    (mS/cm2)\n"
  "  eca = 120  (mV)\n"
  "}\n"
  "    \n"
  "ASSIGNED { \n"
  "  ica (mA/cm2)    \n"
  "  v   (mV)\n"
  "}\n"
  "\n"
  "PROCEDURE iassign () { ica = (1e-3) * gca * mcainf(v)^2 * (v-eca) }\n"
  "\n"
  "INITIAL {\n"
  "  iassign()\n"
  "}\n"
  "\n"
  "BREAKPOINT { iassign() }\n"
  "\n"
  "FUNCTION mcainf(v(mV)) { mcainf = fun2(v, -20, 1,  -9)*1(ms) }\n"
  "\n"
  ":::INCLUDE \"aux_fun.inc\"\n"
  ":::realpath /ddn/jchen/dev/pubtk/pubtk/examples/mod/aux_fun.inc\n"
  ": $Id: aux_fun.inc,v 1.1 2009/11/04 01:24:52 samn Exp $ \n"
  "COMMENT\n"
  "\n"
  "//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
  "//\n"
  "// NOTICE OF COPYRIGHT AND OWNERSHIP OF SOFTWARE\n"
  "//\n"
  "// Copyright 2007, The University Of Pennsylvania\n"
  "// 	School of Engineering & Applied Science.\n"
  "//   All rights reserved.\n"
  "//   For research use only; commercial use prohibited.\n"
  "//   Distribution without permission of Maciej T. Lazarewicz not permitted.\n"
  "//   mlazarew@seas.upenn.edu\n"
  "//\n"
  "//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
  "\n"
  "ENDCOMMENT\n"
  "\n"
  "\n"
  "\n"
  ":-------------------------------------------------------------------\n"
  "FUNCTION fun1(v(mV),V0(mV),A(/ms),B(mV))(/ms) {\n"
  "\n"
  "	 fun1 = A*exp((v-V0)/B)\n"
  "}\n"
  "\n"
  "FUNCTION fun2(v(mV),V0(mV),A(/ms),B(mV))(/ms) {\n"
  "\n"
  "	 fun2 = A/(exp((v-V0)/B)+1)\n"
  "}\n"
  "\n"
  "FUNCTION fun3(v(mV),V0(mV),A(/ms),B(mV))(/ms) {\n"
  "\n"
  "    if(fabs((v-V0)/B)<1e-6) {\n"
  "    :if(v==V0) {\n"
  "        fun3 = A*B/1(mV) * (1- 0.5 * (v-V0)/B)\n"
  "    } else {\n"
  "        fun3 = A/1(mV)*(v-V0)/(exp((v-V0)/B)-1)\n"
  "    }\n"
  "}\n"
  "\n"
  "FUNCTION min(x,y) { if (x<=y){ min = x }else{ min = y } }\n"
  "FUNCTION max(x,y) { if (x>=y){ max = x }else{ max = y } }\n"
  ":::end INCLUDE aux_fun.inc\n"
  ;
#endif
