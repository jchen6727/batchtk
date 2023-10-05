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
 
#define nrn_init _nrn_init__MyExp2SynNMDABB
#define _nrn_initial _nrn_initial__MyExp2SynNMDABB
#define nrn_cur _nrn_cur__MyExp2SynNMDABB
#define _nrn_current _nrn_current__MyExp2SynNMDABB
#define nrn_jacob _nrn_jacob__MyExp2SynNMDABB
#define nrn_state _nrn_state__MyExp2SynNMDABB
#define _net_receive _net_receive__MyExp2SynNMDABB 
#define state state__MyExp2SynNMDABB 
 
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
#define tau1 _p[0]
#define tau1_columnindex 0
#define tau2 _p[1]
#define tau2_columnindex 1
#define tau1NMDA _p[2]
#define tau1NMDA_columnindex 2
#define tau2NMDA _p[3]
#define tau2NMDA_columnindex 3
#define e _p[4]
#define e_columnindex 4
#define r _p[5]
#define r_columnindex 5
#define smax _p[6]
#define smax_columnindex 6
#define sNMDAmax _p[7]
#define sNMDAmax_columnindex 7
#define Vwt _p[8]
#define Vwt_columnindex 8
#define i _p[9]
#define i_columnindex 9
#define iNMDA _p[10]
#define iNMDA_columnindex 10
#define s _p[11]
#define s_columnindex 11
#define sNMDA _p[12]
#define sNMDA_columnindex 12
#define A _p[13]
#define A_columnindex 13
#define B _p[14]
#define B_columnindex 14
#define A2 _p[15]
#define A2_columnindex 15
#define B2 _p[16]
#define B2_columnindex 16
#define mgblock _p[17]
#define mgblock_columnindex 17
#define factor _p[18]
#define factor_columnindex 18
#define factor2 _p[19]
#define factor2_columnindex 19
#define etime _p[20]
#define etime_columnindex 20
#define DA _p[21]
#define DA_columnindex 21
#define DB _p[22]
#define DB_columnindex 22
#define DA2 _p[23]
#define DA2_columnindex 23
#define DB2 _p[24]
#define DB2_columnindex 24
#define v _p[25]
#define v_columnindex 25
#define _g _p[26]
#define _g_columnindex 26
#define _tsav _p[27]
#define _tsav_columnindex 27
#define _nd_area  *_ppvar[0]._pval
 
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

 extern Prop* nrn_point_prop_;
 static int _pointtype;
 static void* _hoc_create_pnt(Object* _ho) { void* create_point_process(int, Object*);
 return create_point_process(_pointtype, _ho);
}
 static void _hoc_destroy_pnt(void*);
 static double _hoc_loc_pnt(void* _vptr) {double loc_point_process(int, void*);
 return loc_point_process(_pointtype, _vptr);
}
 static double _hoc_has_loc(void* _vptr) {double has_loc_point(void*);
 return has_loc_point(_vptr);
}
 static double _hoc_get_loc_pnt(void* _vptr) {
 double get_loc_point_process(void*); return (get_loc_point_process(_vptr));
}
 extern void _nrn_setdata_reg(int, void(*)(Prop*));
 static void _setdata(Prop* _prop) {
 _extcall_prop = _prop;
 }
 static void _hoc_setdata(void* _vptr) { Prop* _prop;
 _prop = ((Point_process*)_vptr)->_prop;
   _setdata(_prop);
 }
 /* connect user functions to hoc names */
 static VoidFunc hoc_intfunc[] = {
 0,0
};
 static Member_func _member_func[] = {
 "loc", _hoc_loc_pnt,
 "has_loc", _hoc_has_loc,
 "get_loc", _hoc_get_loc_pnt,
 0, 0
};
 /* declare global and static user variables */
#define mg mg_MyExp2SynNMDABB
 double mg = 1;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 "tau2", 1e-09, 1e+09,
 "tau1", 1e-09, 1e+09,
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "tau1", "ms",
 "tau2", "ms",
 "tau1NMDA", "ms",
 "tau2NMDA", "ms",
 "e", "mV",
 "smax", "1",
 "sNMDAmax", "1",
 "A", "1",
 "B", "1",
 "A2", "1",
 "B2", "1",
 "i", "nA",
 "iNMDA", "nA",
 "s", "1",
 "sNMDA", "1",
 0,0
};
 static double A20 = 0;
 static double A0 = 0;
 static double B20 = 0;
 static double B0 = 0;
 static double delta_t = 0.01;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "mg_MyExp2SynNMDABB", &mg_MyExp2SynNMDABB,
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
 static void _hoc_destroy_pnt(void* _vptr) {
   destroy_point_process(_vptr);
}
 
static int _ode_count(int);
static void _ode_map(int, double**, double**, double*, Datum*, double*, int);
static void _ode_spec(NrnThread*, _Memb_list*, int);
static void _ode_matsol(NrnThread*, _Memb_list*, int);
 
#define _cvode_ieq _ppvar[2]._i
 static void _ode_matsol_instance1(_threadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"MyExp2SynNMDABB",
 "tau1",
 "tau2",
 "tau1NMDA",
 "tau2NMDA",
 "e",
 "r",
 "smax",
 "sNMDAmax",
 "Vwt",
 0,
 "i",
 "iNMDA",
 "s",
 "sNMDA",
 0,
 "A",
 "B",
 "A2",
 "B2",
 0,
 0};
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
  if (nrn_point_prop_) {
	_prop->_alloc_seq = nrn_point_prop_->_alloc_seq;
	_p = nrn_point_prop_->param;
	_ppvar = nrn_point_prop_->dparam;
 }else{
 	_p = nrn_prop_data_alloc(_mechtype, 28, _prop);
 	/*initialize range parameters*/
 	tau1 = 0.1;
 	tau2 = 10;
 	tau1NMDA = 15;
 	tau2NMDA = 150;
 	e = 0;
 	r = 1;
 	smax = 1e+09;
 	sNMDAmax = 1e+09;
 	Vwt = 0;
  }
 	_prop->param = _p;
 	_prop->param_size = 28;
  if (!nrn_point_prop_) {
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 3, _prop);
  }
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 0,0
};
 static void _net_receive(Point_process*, double*, double);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _MyExp2SynNMDABB_reg() {
	int _vectorized = 1;
  _initlists();
 	_pointtype = point_register_mech(_mechanism,
	 nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init,
	 hoc_nrnpointerindex, 1,
	 _hoc_create_pnt, _hoc_destroy_pnt, _member_func);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
 #if NMODL_TEXT
  hoc_reg_nmodl_text(_mechtype, nmodl_file_text);
  hoc_reg_nmodl_filename(_mechtype, nmodl_filename);
#endif
  hoc_register_prop_size(_mechtype, 28, 3);
  hoc_register_dparam_semantics(_mechtype, 0, "area");
  hoc_register_dparam_semantics(_mechtype, 1, "pntproc");
  hoc_register_dparam_semantics(_mechtype, 2, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 pnt_receive[_mechtype] = _net_receive;
 pnt_receive_size[_mechtype] = 1;
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 MyExp2SynNMDABB /ddn/jchen/dev/pubtk/pubtk/examples/mod/MyExp2SynNMDABB.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[4], _dlist1[4];
 static int state(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) {int _reset = 0; {
   DA = - A / tau1 ;
   DB = - B / tau2 ;
   DA2 = - A2 / tau1NMDA ;
   DB2 = - B2 / tau2NMDA ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) {
 DA = DA  / (1. - dt*( ( - 1.0 ) / tau1 )) ;
 DB = DB  / (1. - dt*( ( - 1.0 ) / tau2 )) ;
 DA2 = DA2  / (1. - dt*( ( - 1.0 ) / tau1NMDA )) ;
 DB2 = DB2  / (1. - dt*( ( - 1.0 ) / tau2NMDA )) ;
  return 0;
}
 /*END CVODE*/
 static int state (double* _p, Datum* _ppvar, Datum* _thread, NrnThread* _nt) { {
    A = A + (1. - exp(dt*(( - 1.0 ) / tau1)))*(- ( 0.0 ) / ( ( - 1.0 ) / tau1 ) - A) ;
    B = B + (1. - exp(dt*(( - 1.0 ) / tau2)))*(- ( 0.0 ) / ( ( - 1.0 ) / tau2 ) - B) ;
    A2 = A2 + (1. - exp(dt*(( - 1.0 ) / tau1NMDA)))*(- ( 0.0 ) / ( ( - 1.0 ) / tau1NMDA ) - A2) ;
    B2 = B2 + (1. - exp(dt*(( - 1.0 ) / tau2NMDA)))*(- ( 0.0 ) / ( ( - 1.0 ) / tau2NMDA ) - B2) ;
   }
  return 0;
}
 
static void _net_receive (Point_process* _pnt, double* _args, double _lflag) 
{  double* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   _thread = (Datum*)0; _nt = (NrnThread*)_pnt->_vnt;   _p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
  if (_tsav > t){ extern char* hoc_object_name(); hoc_execerror(hoc_object_name(_pnt->ob), ":Event arrived out of order. Must call ParallelContext.set_maxstep AFTER assigning minimum NetCon.delay");}
 _tsav = t; {
   double _lww ;
 _lww = _args[0] ;
   if ( r >= 0.0 ) {
       if (nrn_netrec_state_adjust && !cvode_active_){
    /* discon state adjustment for cnexp case (rate uses no local variable) */
    double __state = A;
    double __primary = (A + factor * _lww) - __state;
     __primary += ( 1. - exp( 0.5*dt*( ( - 1.0 ) / tau1 ) ) )*( - ( 0.0 ) / ( ( - 1.0 ) / tau1 ) - __primary );
    A += __primary;
  } else {
 A = A + factor * _lww ;
       }
   if (nrn_netrec_state_adjust && !cvode_active_){
    /* discon state adjustment for cnexp case (rate uses no local variable) */
    double __state = B;
    double __primary = (B + factor * _lww) - __state;
     __primary += ( 1. - exp( 0.5*dt*( ( - 1.0 ) / tau2 ) ) )*( - ( 0.0 ) / ( ( - 1.0 ) / tau2 ) - __primary );
    B += __primary;
  } else {
 B = B + factor * _lww ;
       }
   if (nrn_netrec_state_adjust && !cvode_active_){
    /* discon state adjustment for cnexp case (rate uses no local variable) */
    double __state = A2;
    double __primary = (A2 + factor2 * _lww * r) - __state;
     __primary += ( 1. - exp( 0.5*dt*( ( - 1.0 ) / tau1NMDA ) ) )*( - ( 0.0 ) / ( ( - 1.0 ) / tau1NMDA ) - __primary );
    A2 += __primary;
  } else {
 A2 = A2 + factor2 * _lww * r ;
       }
   if (nrn_netrec_state_adjust && !cvode_active_){
    /* discon state adjustment for cnexp case (rate uses no local variable) */
    double __state = B2;
    double __primary = (B2 + factor2 * _lww * r) - __state;
     __primary += ( 1. - exp( 0.5*dt*( ( - 1.0 ) / tau2NMDA ) ) )*( - ( 0.0 ) / ( ( - 1.0 ) / tau2NMDA ) - __primary );
    B2 += __primary;
  } else {
 B2 = B2 + factor2 * _lww * r ;
       }
 }
   else {
     if ( r > - 1000.0 ) {
         if (nrn_netrec_state_adjust && !cvode_active_){
    /* discon state adjustment for cnexp case (rate uses no local variable) */
    double __state = A2;
    double __primary = (A2 - factor2 * _lww * r) - __state;
     __primary += ( 1. - exp( 0.5*dt*( ( - 1.0 ) / tau1NMDA ) ) )*( - ( 0.0 ) / ( ( - 1.0 ) / tau1NMDA ) - __primary );
    A2 += __primary;
  } else {
 A2 = A2 - factor2 * _lww * r ;
         }
   if (nrn_netrec_state_adjust && !cvode_active_){
    /* discon state adjustment for cnexp case (rate uses no local variable) */
    double __state = B2;
    double __primary = (B2 - factor2 * _lww * r) - __state;
     __primary += ( 1. - exp( 0.5*dt*( ( - 1.0 ) / tau2NMDA ) ) )*( - ( 0.0 ) / ( ( - 1.0 ) / tau2NMDA ) - __primary );
    B2 += __primary;
  } else {
 B2 = B2 - factor2 * _lww * r ;
         }
 }
     }
   } }
 
static int _ode_count(int _type){ return 4;}
 
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
	for (_i=0; _i < 4; ++_i) {
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
  A2 = A20;
  A = A0;
  B2 = B20;
  B = B0;
 {
   double _ltp ;
 Vwt = 0.0 ;
   if ( tau1 / tau2 > .9999 ) {
     tau1 = .9999 * tau2 ;
     }
   A = 0.0 ;
   B = 0.0 ;
   _ltp = ( tau1 * tau2 ) / ( tau2 - tau1 ) * log ( tau2 / tau1 ) ;
   factor = - exp ( - _ltp / tau1 ) + exp ( - _ltp / tau2 ) ;
   factor = 1.0 / factor ;
   if ( tau1NMDA / tau2NMDA > .9999 ) {
     tau1NMDA = .9999 * tau2NMDA ;
     }
   A2 = 0.0 ;
   B2 = 0.0 ;
   _ltp = ( tau1NMDA * tau2NMDA ) / ( tau2NMDA - tau1NMDA ) * log ( tau2NMDA / tau1NMDA ) ;
   factor2 = - exp ( - _ltp / tau1NMDA ) + exp ( - _ltp / tau2NMDA ) ;
   factor2 = 1.0 / factor2 ;
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
 _tsav = -1e20;
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
   mgblock = 1.0 / ( 1.0 + 0.28 * exp ( - 0.062 * v ) ) ;
   s = B - A ;
   sNMDA = B2 - A2 ;
   if ( s > smax ) {
     s = smax ;
     }
   if ( sNMDA > sNMDAmax ) {
     sNMDA = sNMDAmax ;
     }
   i = s * ( v - e ) ;
   iNMDA = sNMDA * ( v - e ) * mgblock ;
   }
 _current += i;
 _current += iNMDA;

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
 _g *=  1.e2/(_nd_area);
 _rhs *= 1.e2/(_nd_area);
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
 {   state(_p, _ppvar, _thread, _nt);
  }}}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = A_columnindex;  _dlist1[0] = DA_columnindex;
 _slist1[1] = B_columnindex;  _dlist1[1] = DB_columnindex;
 _slist1[2] = A2_columnindex;  _dlist1[2] = DA2_columnindex;
 _slist1[3] = B2_columnindex;  _dlist1[3] = DB2_columnindex;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif

#if NMODL_TEXT
static const char* nmodl_filename = "/ddn/jchen/dev/pubtk/pubtk/examples/mod/MyExp2SynNMDABB.mod";
static const char* nmodl_file_text = 
  ": $Id: MyExp2SynNMDABB.mod,v 1.4 2010/12/13 21:28:02 samn Exp $ \n"
  "NEURON {\n"
  ":  THREADSAFE\n"
  "  POINT_PROCESS MyExp2SynNMDABB\n"
  "  RANGE tau1, tau2, e, i, iNMDA, s, sNMDA, r, tau1NMDA, tau2NMDA, Vwt, smax, sNMDAmax\n"
  "  NONSPECIFIC_CURRENT i, iNMDA\n"
  "}\n"
  "\n"
  "UNITS {\n"
  "  (nA) = (nanoamp)\n"
  "  (mV) = (millivolt)\n"
  "  (uS) = (microsiemens)\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "  tau1     =   0.1 (ms) <1e-9,1e9>\n"
  "  tau2     =  10 (ms) <1e-9,1e9>	\n"
  "  tau1NMDA = 15  (ms)\n"
  "  tau2NMDA = 150 (ms)\n"
  "  e        = 0	(mV)\n"
  "  mg       = 1\n"
  "  r        = 1\n"
  "  smax     = 1e9 (1)\n"
  "  sNMDAmax = 1e9 (1)\n"
  "  \n"
  "  Vwt   = 0 : weight for inputs coming in from vector\n"
  "}\n"
  "\n"
  "ASSIGNED {\n"
  "  v       (mV)\n"
  "  i       (nA)\n"
  "  iNMDA   (nA)\n"
  "  s       (1)\n"
  "  sNMDA   (1)\n"
  "  mgblock (1)\n"
  "  factor  (1)\n"
  "  factor2 (1)\n"
  "	\n"
  "  etime (ms)\n"
  "}\n"
  "\n"
  "STATE {\n"
  "  A  (1)\n"
  "  B  (1)\n"
  "  A2 (1)\n"
  "  B2 (1)\n"
  "}\n"
  "\n"
  "INITIAL {\n"
  "\n"
  "  LOCAL tp\n"
  "  \n"
  "  Vwt = 0 : testing\n"
  "\n"
  "  if (tau1/tau2 > .9999) {\n"
  "    tau1 = .9999*tau2\n"
  "  }\n"
  "  A = 0\n"
  "  B = 0	\n"
  "  tp = (tau1*tau2)/(tau2 - tau1) * log(tau2/tau1)\n"
  "  factor = -exp(-tp/tau1) + exp(-tp/tau2)\n"
  "  factor = 1/factor\n"
  "  \n"
  "  if (tau1NMDA/tau2NMDA > .9999) {\n"
  "    tau1NMDA = .9999*tau2NMDA\n"
  "  }\n"
  "  A2 = 0\n"
  "  B2 = 0	\n"
  "  tp = (tau1NMDA*tau2NMDA)/(tau2NMDA - tau1NMDA) * log(tau2NMDA/tau1NMDA)\n"
  "  factor2 = -exp(-tp/tau1NMDA) + exp(-tp/tau2NMDA)\n"
  "  factor2 = 1/factor2  \n"
  "}\n"
  "\n"
  "BREAKPOINT {\n"
  "  SOLVE state METHOD cnexp\n"
  "  : Jahr Stevens 1990 J. Neurosci\n"
  "  mgblock = 1.0 / (1.0 + 0.28 * exp(-0.062(/mV) * v) )\n"
  "  s     = B  - A\n"
  "  sNMDA = B2 - A2\n"
  "  if (s    >smax)     {s    =smax    }: saturation\n"
  "  if (sNMDA>sNMDAmax) {sNMDA=sNMDAmax}: saturation\n"
  "  i     = s     * (v - e) \n"
  "  iNMDA = sNMDA * (v - e) * mgblock\n"
  "}\n"
  "\n"
  "DERIVATIVE state {\n"
  "  A'  = -A/tau1\n"
  "  B'  = -B/tau2	\n"
  "  A2' = -A2/tau1NMDA\n"
  "  B2' = -B2/tau2NMDA\n"
  "}\n"
  "\n"
  "NET_RECEIVE(w (uS)) {LOCAL ww\n"
  "  ww=w\n"
  "  :printf(\"NMDA Spike: %g\\n\", t)\n"
  "  if(r>=0){ : if r>=0, g = AMPA + NMDA*r\n"
  "    A  = A  + factor *ww\n"
  "    B  = B  + factor *ww\n"
  "    A2 = A2 + factor2*ww*r\n"
  "    B2 = B2 + factor2*ww*r\n"
  "  }else{\n"
  "    if(r>-1000){ : if r>-1, g = NMDA*r  \n"
  "      A2 = A2 - factor2*ww*r\n"
  "      B2 = B2 - factor2*ww*r\n"
  "    }\n"
  "    : if r<0 and r<>-1, g = 0\n"
  "  }\n"
  "}\n"
  ;
#endif
