#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;
#if defined(__cplusplus)
extern "C" {
#endif

extern void _CA1ih_reg(void);
extern void _CA1ika_reg(void);
extern void _CA1ikdr_reg(void);
extern void _CA1ina_reg(void);
extern void _caolmw_reg(void);
extern void _icaolmw_reg(void);
extern void _iholmw_reg(void);
extern void _kcaolmw_reg(void);
extern void _kdrbwb_reg(void);
extern void _MyExp2SynBB_reg(void);
extern void _MyExp2SynNMDABB_reg(void);
extern void _nafbwb_reg(void);

void modl_reg() {
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");
    fprintf(stderr, " \"mod/CA1ih.mod\"");
    fprintf(stderr, " \"mod/CA1ika.mod\"");
    fprintf(stderr, " \"mod/CA1ikdr.mod\"");
    fprintf(stderr, " \"mod/CA1ina.mod\"");
    fprintf(stderr, " \"mod/caolmw.mod\"");
    fprintf(stderr, " \"mod/icaolmw.mod\"");
    fprintf(stderr, " \"mod/iholmw.mod\"");
    fprintf(stderr, " \"mod/kcaolmw.mod\"");
    fprintf(stderr, " \"mod/kdrbwb.mod\"");
    fprintf(stderr, " \"mod/MyExp2SynBB.mod\"");
    fprintf(stderr, " \"mod/MyExp2SynNMDABB.mod\"");
    fprintf(stderr, " \"mod/nafbwb.mod\"");
    fprintf(stderr, "\n");
  }
  _CA1ih_reg();
  _CA1ika_reg();
  _CA1ikdr_reg();
  _CA1ina_reg();
  _caolmw_reg();
  _icaolmw_reg();
  _iholmw_reg();
  _kcaolmw_reg();
  _kdrbwb_reg();
  _MyExp2SynBB_reg();
  _MyExp2SynNMDABB_reg();
  _nafbwb_reg();
}

#if defined(__cplusplus)
}
#endif
