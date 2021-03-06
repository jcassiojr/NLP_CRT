import sys
import cProfile

from model_tester import FeaturePipeline, test_model
from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from baseline_transformer import GetConcatenatedNotesTransformer, GetLatestNotesTransformer, DocumentConcatenatorTransformer, GetEncountersFeaturesTransformer, GetLabsCountsDictTransformer, GetLabsLowCountsDictTransformer, GetLabsHighCountsDictTransformer, GetLabsLatestHighDictTransformer, GetLabsLatestLowDictTransformer, GetLabsHistoryDictTransformer
from extract_data import get_doc_rel_dates, get_operation_date, get_ef_values
from extract_data import get_operation_date,  is_note_doc, get_date_key
from symptoms_extractor import SymptomsExtractorTransformerGenerator
from icd_transformer import ICD9_Transformer
from value_extractor_transformer import EFTransformer, LBBBTransformer, SinusRhythmTransformer, QRSTransformer, NYHATransformer
from language_processing import parse_date 

def main():
    transformer_list = []
    if False:
        transformer_list += SymptomsExtractorTransformerGenerator(['Car','Lno'], 'found', None, 6*30).getSymptoms()
    if False:
        transformer_list += [
                    ('Dia', ICD9_Transformer())
                ]
    if False:
        transformer_list += [ 
                    ('EF', EFTransformer('all', 1, None)),
                    ('EF', EFTransformer('mean', 5, None)),
                    ('EF', EFTransformer('max', 5, None)),
                    ('LBBB', LBBBTransformer()),
                    ('SR', SinusRhythmTransformer()),
                    ('NYHA', NYHATransformer()),
                    ('QRS', QRSTransformer('all', 1, None)),#Bugs with QRS
                ]
    if False:
        transformer_list += [
                    ('Car', FeaturePipeline([
                        ('notes_transformer_car', GetConcatenatedNotesTransformer('Car')),
                        ('tfidf', TfidfTransformer())
                    ])),
                    ('Lno', FeaturePipeline([
                       ('notes_transformer_lno', GetConcatenatedNotesTransformer('Lno')),
                       ('tfidf', TfidfTransformer)
                    ]))
                ]

    if False:
        transformer_list += [
                    #('Car', FeaturePipeline([
                    #    ('notes_transformer_car', GetLatestNotesTransformer('Car', 100)),
                    #    ('notes_aggregator_car', DocumentConcatenatorTransformer()),
                    #    ('trigram', CountVectorizer(ngram_range=(3,3), min_df=2))
                    #])),
                    ('Car', FeaturePipeline([
                        ('notes_transformer_car', GetConcatenatedNotesTransformer('Car')),
                        ('bigram', CountVectorizer(ngram_range=(2,2), min_df=0.05))
                    ])),
                    ('Lno', FeaturePipeline([
                       ('notes_transformer_lno', GetConcatenatedNotesTransformer('Lno')),
                       ('bigram', CountVectorizer(ngram_range=(2,2), min_df=0.05))
                    ]))
                ]


    if True:
        transformer_list += [
                    #('Enc', GetEncountersFeaturesTransformer(100, True)),
                    ('Labs_Counts',FeaturePipeline([
                        ('labs_counts_transformer', GetLabsCountsDictTransformer()),
                        ('dict_vectorizer', DictVectorizer())
                    ])),
                    ('Labs_Low_Counts',FeaturePipeline([
                        ('labs_low_counts_transformer', GetLabsLowCountsDictTransformer()),
                       ('dict_vectorizer', DictVectorizer())
                    ])),
                    ('Labs_High_Counts', FeaturePipeline([
                        ('labs_high_counts_transformer', GetLabsHighCountsDictTransformer()),
                        ('dict_vectorizer', DictVectorizer())
                    ])),
                    #('Labs_Latest_Low', FeaturePipeline([
                    #    ('labs_latest_low_transformer', GetLabsLatestLowDictTransformer()),
                    #    ('dict_vectorizer', DictVectorizer())
                    #])),
                    #('Labs_Latest_High',FeaturePipeline([
                    #    ('labs_latest_high_transformer', GetLabsLatestHighDictTransformer()),
                    #    ('dict_vectorizer', DictVectorizer())
                    #])),
                    #('Labs_History', FeaturePipeline([
                    #    ('labs_history_transformer', GetLabsHistoryDictTransformer([1])),
                    #    ('dict_vectorizer', DictVectorizer())
                    #]))
                ]

    
    features = FeatureUnion(transformer_list)

    if len(sys.argv) > 1 and unicode(sys.argv[1]).isnumeric():
        data_size = min(int(sys.argv[1]), 906)
    else:
        data_size = 25

    if len(sys.argv) > 2 and unicode(sys.argv[2]).isnumeric():
        num_cv_splits = int(sys.argv[2])
    else:
        num_cv_splits = 5

    print "Data size: " + str(data_size)
    print "CV splits: " + str(num_cv_splits)

    #method = 'lr'
    #method = 'svm'
    method = 'adaboost'
    #method = 'cdm'

    model_args = dict()
    if method in ['lr', 'svm']:
        if len(sys.argv) > 3 and unicode(sys.argv[3]).isnumeric():
            model_args['C'] = float(sys.argv[3])
        #else:
            #model_args['C'] = 0.
    if method == 'adaboost':
        if len(sys.argv) > 3 and unicode(sys.argv[3]).isnumeric():
            model_args['n_estimators'] = int(sys.argv[3])
        else:
            model_args['n_estimators'] = 50
        

    show_progress = True
    print 'Method:', method
    test_model(features, data_size, num_cv_splits, method, show_progress, model_args)

if __name__ == '__main__':
    main()
