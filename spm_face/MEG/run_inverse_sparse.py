import pylab as pl

import mne
from mne.inverse_sparse import mixed_norm, tf_mixed_norm
from mne.minimum_norm import apply_inverse, make_inverse_operator
from mne.viz import plot_sparse_source_estimates

###############################################################################
# Set parameters
ave_fname = 'evoked-ave.fif'
cov_fname = 'noise-cov.fif'
fwd_fname = 'SPM_CTF_MEG_example_faces1_3D-meg-oct-6-fwd.fif'

# Read noise covariance matrix
cov = mne.read_cov(cov_fname)
# Handling average file
evoked = mne.fiff.read_evoked(ave_fname, setno='faces', baseline=(None, 0))
# Handling forward solution
forward = mne.read_forward_solution(fwd_fname, surf_ori=True)

pl.figure()
ylim = dict(mag=[-600, 600])
evoked.plot(ylim=ylim, proj=True)

###############################################################################
# Run solver
alpha = 70  # regularization parameter between 0 and 100 (100 is high)
loose, depth = 0.2, 0.8  # loose orientation & depth weighting

# evoked.crop(tmin=0, tmax=0.3)  # only required for mixed_norm

# Compute dSPM solution to be used as weights in MxNE
inverse_operator = make_inverse_operator(evoked.info, forward, cov,
                                         loose=loose, depth=depth, fixed=True)
stc_dspm = apply_inverse(evoked, inverse_operator, lambda2=1. / 9.,
                         method='dSPM')

# # Compute MxNE inverse solution
# stc, residual = mixed_norm(evoked, forward, cov, alpha, loose=loose,
#                  depth=depth, maxit=3000, tol=1e-4, active_set_size=10,
#                  debias=True, weights=stc_dspm, weights_min=8.,
#                  return_residual=True)

# Compute TF-MxNE inverse solution
alpha = 50  # regularization parameter between 0 and 100 (100 is high)
alpha_time = 1.
stc, residual = tf_mixed_norm(evoked, forward, cov, alpha, alpha_time,
                    loose=loose, depth=depth, maxit=200, tol=1e-4,
                    weights=stc_dspm, weights_min=8., debias=True,
                    wsize=16, tstep=4, window=0.05, return_residual=True)

pl.figure()
residual.plot(ylim=ylim, proj=True)

###############################################################################
# View in 2D and 3D ("glass" brain like 3D plot)
plot_sparse_source_estimates(forward['src'], stc, bgcolor=(1, 1, 1),
                     opacity=0.1, fig_name="MxNE (cond %s)" % evoked.comment)