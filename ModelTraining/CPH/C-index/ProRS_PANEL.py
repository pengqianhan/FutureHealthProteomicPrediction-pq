
import numpy as np
import pandas as pd
import pickle
from Utility.Evaluation_Utilities import *
from lifelines import CoxPHFitter
from sklearn.metrics import recall_score, roc_auc_score, confusion_matrix
pd.options.mode.chained_assignment = None  # default='warn'
from lifelines.utils import concordance_index

def preprocess_target_individuals(target_df_file, target_code):
    target_y0, target_yrs0, target_source0 = target_code[0] + '0_y', target_code[0] + '0_years', target_code[0] + '0_source'
    target_y, target_yrs, target_source = target_code + '_y', target_code + '_years', target_code + '_source'
    target_df = pd.read_csv(target_df_file, usecols=['eid', 'Region_code', target_y, target_yrs])
    if (('C' in target_code) | ('X' in target_code)):
        target_df0 = pd.read_csv(target_df_file, usecols=['eid', 'Region_code', target_y0, target_yrs0])
        rm_idx0 = target_df0.index[target_df0[target_yrs0] <= 0]
        rm_eid_lst = target_df0.iloc[rm_idx0].eid.tolist()
    else:
        target_df0 = pd.read_csv(target_df_file, usecols=['eid', 'Region_code', target_y0, target_yrs0, target_source0])
        rm_idx0 = target_df0.index[(target_df0[target_source0] >= 50) | (target_df0[target_yrs0] <= 0)]
        rm_eid_lst = target_df0.iloc[rm_idx0].eid.tolist()
    clean_df = target_df[~target_df.eid.isin(rm_eid_lst)]
    clean_df.reset_index(inplace=True)
    clean_df.drop('index', axis=1, inplace=True)
    return clean_df

dpath = '/Volumes/JasonWork/Projects/UKB_Proteomics/Data/'
outpath = '/Volumes/JasonWork/Projects/UKB_Proteomics/Results/'
target_df_file = dpath + 'PreprocessedData/TargetData/TargetData.csv'
cov_df = pd.read_csv(dpath + 'PreprocessedData/Covariates/PANEL.csv')
cov_df.drop('Region_code', axis = 1, inplace = True)
cov_df['DM_ETH'] = cov_df['DM_ETH_W'] + cov_df['DM_ETH_A']*2 + cov_df['DM_ETH_B']*3 + cov_df['DM_ETH_O']*4 - 1

my_formula = 'ProRS +' \
             'DM_AGE + C(DM_GENDER) + C(DM_ETH) + DM_TDI + DM_EDUC + '\
             'C(LS_ALC) + C(LS_SMK) + C(LS_PA) + C(LS_DIET) + LS_SOC + C(LS_SLP) + '\
             'PM_BMI + PM_BMR + PM_WT + PM_HT + PM_WC + PM_DBP + PM_SBP + '\
             'C(DH_DIAB) + C(DH_HYPT) + C(MH_CHOL) + C(MH_BP) + C(MH_INSU) + '\
             'C(FH_DIAB) + C(FH_HBP) + C(FH_DM) + C(FH_HD) + '\
             'BF_LP_TC + BF_LP_HDLC + BF_LP_LDLC + BF_LP_TRG + '\
             'BF_GL_GL + BF_GL_HBA1C + BF_IF_CRP + BF_EC_IGF1 + BF_EC_SHBG + '\
             'BF_LV_AP + BF_LV_ALT + BF_LV_AST + BF_LV_GGT + '\
             'BF_RE_ALB + BF_RE_TPRO + BF_RE_CR + BF_RE_CYSC + BF_RE_UREA + '\
             'BF_BC_WBC + BF_BC_RBC + BF_BC_HB + BF_BC_HCT + BF_BC_MCV + BF_BC_MCH + BF_BC_PLT'

target_code_df = pd.read_csv(dpath + 'Target_code.csv', encoding='latin-1')
target_code_lst = target_code_df.Disease_code.tolist()
fold_id_lst = [ele for ele in range(10)]

out_cidx_lst = []

for target_code in target_code_lst:
    cidx_lst = []
    for fold_id in fold_id_lst:
        prors_train = pd.read_csv(outpath + 'MLModeling/MLP/ResMLP/' + target_code + '/Train' + str(fold_id) + '_ProRS.csv')
        mydf_train = pd.merge(prors_train, cov_df, how = 'inner', on = ['eid'])
        prors_test = pd.read_csv(outpath + 'MLModeling/MLP/ResMLP/' + target_code + '/Test' + str(fold_id) + '_ProRS.csv')
        mydf_test = pd.merge(prors_test, cov_df, how = 'inner', on = ['eid'])
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(mydf_train, duration_col='Y_yrs', event_col='Y', formula=my_formula)
        try:
            cidx_lst.append(concordance_index(mydf_test['Y_yrs'], -cph.predict_partial_hazard(mydf_test), mydf_test['Y']))
        except:
            cidx_lst.append(np.mean(cidx_lst))
            print((target_code, fold_id))
    out_cidx_lst.append([target_code, np.mean(cidx_lst), np.std(cidx_lst)] + cidx_lst)
    out_df = pd.DataFrame(out_cidx_lst)
    out_df.columns = ['Disease_code', 'C_idx_mean', 'C_idx_std'] + ['C_idx_region' + str(ele) for ele in fold_id_lst]
    out_df = pd.merge(target_code_df, out_df, how='left', on=['Disease_code'])
    out_df.to_csv(outpath + 'MLModeling/CPH/Combo/ProRS_PANEL_Cidx.csv', index=False)
    print((target_code, np.mean(cidx_lst)))



