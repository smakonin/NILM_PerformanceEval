#
# A library of Accuracy functions (Library_Accuracy.py)
# Copyright (C) 2014 Stephen Makonin. All Right Reserved.
#
# NILM performance evaluation functions use in the Springer Energy Efficiency journal paper.
# The paper DOI 10.1007/s12053-014-9306-2
#
# For use with Python 3
#

from math import sqrt

loads = 0
folds = 0
trials = []

classify_inacc = []
classify_atp = []
classify_itp = []
classify_tp = []
classify_tn = []
classify_fp = []
classify_fn = []

measure_est = []
measure_truth = []
measure_diff = []
measure_diff_sq = []

#
# Setup the gloabal accuracy collecting valiables
#
# _loads: the number of loads being disaggregated
# _folds: The number of folds using to test, usually 10
#
def setup_accuracy(_loads, _folds):
    global loads, folds, trials, classify_inacc, classify_atp, classify_itp, classify_tp, classify_tn, classify_fp, classify_fn, measure_est, measure_truth, measure_diff, measure_diff_sq
    
    loads = _loads
    folds = _folds
    trials = [0 for s in range(folds)]

    classify_inacc = [[0.0 for s in range(folds)] for i in range(loads)]
    classify_atp = [[0.0 for s in range(folds)] for i in range(loads)]
    classify_itp = [[0.0 for s in range(folds)] for i in range(loads)]
    classify_tp = [[0.0 for s in range(folds)] for i in range(loads)]
    classify_tn = [[0.0 for s in range(folds)] for i in range(loads)]
    classify_fp = [[0.0 for s in range(folds)] for i in range(loads)]
    classify_fn = [[0.0 for s in range(folds)] for i in range(loads)]
        
    measure_est = [[0 for s in range(folds)] for i in range(loads)]
    measure_truth = [[0 for s in range(folds)] for i in range(loads)]
    measure_diff = [[0 for s in range(folds)] for i in range(loads)]
    measure_diff_sq = [[0 for s in range(folds)] for i in range(loads)]

#
# Record the state classification outcome
# 
# fold:   the testing fold you are on
# est:    the estimated state of the load
# truth:  the ground truth state of the load
# states: the number of states for that load
#
def record_classification_result(fold, est, truth, states):   
    global loads, folds, trials, classify_inacc, classify_tp, classify_tn, classify_fp, classify_fn

    trials[fold] += 1

    for load in range(loads):
        if est[load] > 0 and truth[load] > 0:
            classify_inacc[load][fold] += float(abs(est[load] - truth[load])) / float(states[load])
            classify_tp[load][fold] += 1.0
        elif est[load] == 0 and truth[load] == 0:
            classify_tn[load][fold] += 1.0
        elif est[load] > 0 and truth[load] == 0:
            classify_fp[load][fold] += 1.0
        elif est[load] == 0 and truth[load] > 0:
            classify_fn[load][fold] += 1.0
        else:
            print("EORROR impossible FS f-score case!")
            exit(1)

#
# Record the estimated consumtion outcome
# 
# fold:   the testing fold you are on
# est:    the estimated consumtion amount of the load
# truth:  the ground truth consumtion amount of the load
#            
def record_measurement_result(fold, est, truth):
    global loads, folds, measure_est, measure_truth, measure_diff, measure_diff_sq, classify_atp, classify_itp
    
    for load in range(loads):
        measure_est[load][fold] += est[load]
        measure_truth[load][fold] += truth[load]
        measure_diff[load][fold] += abs(est[load] - truth[load])
        measure_diff_sq[load][fold] += (truth[load] - est[load]) ** 2
        
        rho = 0.2
        if est[load] > 0.0 and truth[load] > 0.0:
            if float(abs(est[load] - truth[load])) / float(truth[load]) <= rho:
                classify_atp[load][fold] += 1.0
            else:
                classify_itp[load][fold] += 1.0

#
# Create CSV of accuracy results data for loading saving and speadsheet use
# 
# test_id: the testing ID you are using
# labels:  the name list of load
# measure: the demand measure used, e.g. A, W, VAR, etc
#
def accuracy_csv(test_id, labels, measure):
    hdr = 'Test ID, Load, Correct, Incorrect, TP, Inacc, APT, ITP, TN, FP, FN, Basic Acc, Precision, Recall, F-Score, M Precision, M Recall, M F-Score, FS Precision, FS Recall, FS F-Score, RMSE, NDE, Kolter, Est Acc, Estimated, Actual, Diff, Est of Total, Actual of Total'
    det = ''
    for i in range(-1, loads):
        label = '*TL'
        if i > -1:
            label = labels[i]
        det += ', '.join([str(v) for v in [test_id, label, correct(i), incorrect(i), tp(i), inacc(i), atp(i), itp(i), tn(i), fp(i), fn(i), accuracy(i), precision(i), recall(i), fscore(i), m_precision(i), m_recall(i), m_fscore(i), fs_precision(i), fs_recall(i), fs_fscore(i), rmse(i), nde(i), kolter(i), estacc(i), est(i), truth(i), diff(i), est_percent(i), truth_percent(i)]]) + '\n'
    
    return (hdr, det)

#
# Print an accuracy results report to the screen
# 
# labels:  the name list of load
# measure: the demand measure used, e.g. A, W, VAR, etc
#
def print_accuracy(labels, measure):   
    print()
    print()
    print('Classification & Esitmation Accuracies:')
    print()
    print('\tAccuracy     = %6.2f%% (%d incorrect tests)' % (accuracy() * 100., incorrect()))    
    print('\tPrecision    = %6.2f%%' % (precision() * 100.))
    print('\tRecall       = %6.2f%%' % (recall() * 100.))
    print('\tF-Score      = %6.2f%%' % (fscore() * 100.))

    print()
    print('\tM Precision  = %6.2f%%' % (m_precision() * 100.))
    print('\tM Recall     = %6.2f%%' % (m_recall() * 100.))
    print('\tM F-Score    = %6.2f%%' % (m_fscore() * 100.))

    print()
    print('\tFS Precision = %6.2f%%' % (fs_precision() * 100.))
    print('\tFS Recall    = %6.2f%%' % (fs_recall() * 100.))
    print('\tFS F-Score   = %6.2f%%' % (fs_fscore() * 100.))
    print()
    print('\tNDE          = %6.2f%%' % (nde() * 100.))
    print('\tRMSE         = %6.2f' % (rmse()))
    print('\tEsitmation   = %6.2f%% (%d %s difference)' % (estacc() * 100., diff(), measure))
    print()

    print('\t|----------|----------|---------|-----------|----------|-------------------------------|------------|-------------------|')
    print('\t|          |          |         |           |          | FINITE-STATE MODIFICATIONS:   |            | PRECENT OF TOTAL: |')
    print('\t| LOAD ID  | ACCURACY |     NDE |   F-SCORE | M-FSCORE | PRECISION |  RECALL | F-SCORE | ESITMATION |     EST |   TRUTH |')
    print('\t|----------|----------|---------|-----------|----------|-----------|---------|---------|------------|---------|---------|')
    for i in range(loads):
        print('\t| %-8s |  %6.2f%% | %6.2f%% |   %6.2f%% |  %6.2f%% |   %6.2f%% | %6.2f%% | %6.2f%% |    %6.2f%% | %6.2f%% | %6.2f%% |' % (labels[i], accuracy(i) * 100., nde(i) * 100., fscore(i), m_fscore(i) * 100., fs_precision(i) * 100., fs_recall(i) * 100., fs_fscore(i) * 100., estacc(i) * 100., est_percent(i) * 100., truth_percent(i) * 100.))
    print('\t|----------|----------|---------|-----------|----------|-----------|---------|---------|------------|=========|=========|')
    print('\t                                                                                                    | 100.00% | 100.00% |')
    print('\t                                                                                                    |---------|---------|')
    print()        


#
# Fun lambda functions for calculating different accuracy measures
#

quotient         = lambda n, d: 0.0 if d == 0.0 else float(n) / float(d)
mean             = lambda a: float(sum(a)) / float(len(a))

inacc            = lambda m = -1: round(mean(classify_inacc[m]), 4) if m >= 0 else sum([inacc(i) for i in range(loads)])
atp              = lambda m = -1: int(mean(classify_atp[m])) if m >= 0 else sum([atp(i) for i in range(loads)])
itp              = lambda m = -1: int(mean(classify_itp[m])) if m >= 0 else sum([itp(i) for i in range(loads)])
tp               = lambda m = -1: int(mean(classify_tp[m])) if m >= 0 else sum([tp(i) for i in range(loads)])
hit              = lambda m = -1: tp(m)
tn               = lambda m = -1: int(mean(classify_tn[m])) if m >= 0 else sum([tn(i) for i in range(loads)])
corr_reject      = lambda m = -1: tn(m)
fp               = lambda m = -1: int(mean(classify_fp[m])) if m >= 0 else sum([fp(i) for i in range(loads)])
false_alarm      = lambda m = -1: fp(m)
typeI_error      = lambda m = -1: fp(m)
fn               = lambda m = -1: int(mean(classify_fn[m])) if m >= 0 else sum([fn(i) for i in range(loads)])
miss             = lambda m = -1: fn(m)
typeII_error     = lambda m = -1: fn(m)
correct          = lambda m = -1: tp(m) + tn(m)
incorrect        = lambda m = -1: fp(m) + fn(m)
tp_rate          = lambda m = -1: round(quotient(tp(m), tp(m) + fn(m)), 4)
sensitivity      = lambda m = -1: tp_rate(m)
recall           = lambda m = -1: tp_rate(m)
hit_rate         = lambda m = -1: tp_rate(m)
tn_rate          = lambda m = -1: round(quotient(tn(m), fp(m) + tn(m)), 4)
specificity      = lambda m = -1: tn_rate(m)
precision        = lambda m = -1: round(quotient(tp(m), tp(m) + fp(m)), 4)
pos_predictive   = lambda m = -1: precision(m)
neg_predictive   = lambda m = -1: round(quotient(tn(m), tn(m) + fn(m)), 4)
fp_rate          = lambda m = -1: round(quotient(fp(m), fp(m) + tn(m)), 4)
fall_out         = lambda m = -1: fp_rate(m)
fn_rate          = lambda m = -1: round(quotient(fn(m), fn(m) + tp(m)), 4)
miss_rate        = lambda m = -1: fn_rate(m)
false_discovery  = lambda m = -1: round(quotient(fp(m), tp(m) + fp(m)), 4)
accuracy         = lambda m = -1: round(quotient(correct(m), correct(m) + incorrect(m)), 4)
fscore           = lambda m = -1: round(2.0 * quotient(precision(m) * recall(m), precision(m) + recall(m)), 4)
matthews_correl  = lambda m = -1: round(quotient(tp(m) * tn(m) + fp(m) * fn(m), sqrt((tp(m) + fp(m)) * (tp(m) + fn(m)) * (tn(m) + fp(m)) * (tn(m) + fn(m)))), 4)
informedness     = lambda m = -1: round(tp_rate(m) + tn_rate(m) - 1.0, 4)
markedness       = lambda m = -1: round(pos_predictive(m) + neg_predictive(m) - 1.0, 4)
nde              = lambda m = -1: round(quotient(abs(est(m) - truth(m)), truth(m)), 4)
rmse             = lambda m = -1: round(sqrt(quotient(1.0, mean(trials)) * mean(measure_diff_sq[m])) if m >= 0 else sum([rmse(i) for i in range(loads)]), 4)
diff             = lambda m = -1: round(mean(measure_diff[m]) if m >= 0 else sum([diff(i) for i in range(loads)]), 2)
est              = lambda m = -1: round(mean(measure_est[m]) if m >= 0 else sum([est(i) for i in range(loads)]), 2)
truth            = lambda m = -1: round(mean(measure_truth[m]) if m >= 0 else sum([truth(i) for i in range(loads)]), 2)
kolter           = lambda m = -1: round(1.0 - quotient(diff(m), 2.0 * truth(m)), 4)

m_precision      = lambda m = -1: round(quotient(atp(m), atp(m) + itp(m) + fp(m)), 4)
m_recall         = lambda m = -1: round(quotient(atp(m), atp(m) + itp(m) + fn(m)), 4)
m_fscore         = lambda m = -1: round(2.0 * quotient(m_precision(m) * m_recall(m), m_precision(m) + m_recall(m)), 4)

fs_precision     = lambda m = -1: round(quotient(tp(m) - inacc(m), tp(m) + fp(m)), 4)
fs_recall        = lambda m = -1: round(quotient(tp(m) - inacc(m), tp(m) + fn(m)), 4)
fs_fscore        = lambda m = -1: round(2.0 * quotient(fs_precision(m) * fs_recall(m), fs_precision(m) + fs_recall(m)), 4)
estacc           = lambda m = -1: round(kolter(m), 4)

est_percent      = lambda m: round(float(est(m)) / float(est()), 4)
truth_percent    = lambda m: round(float(truth(m)) / float(truth()), 4)

