# various default settings used across scripts
# {group: {param_name:
#   (type|(list, type), default, model_type, help, choices)}}
PARAMS = {'data':
          # * everything data-related *
          {'data_source':
           (str, 'genes', None,
            'dataset type to use', ['genes', 'fragments']),
           'classes':
           ((list, str),
            ["Gempylidae", "Salmonidae", "Holocentridae", "Gastromyzontidae", "Istiophoridae", "Girellidae", "Nototheniidae", "Nothobranchiidae", "Kneriidae", "Muraenidae", "Bagridae", "Cyprinidae", "Cyclopteridae", "Nemacheilidae", "Serranidae", "Macrouridae", "Anguillidae", "Syngnathidae", "Leuciscidae", "Acipenseridae", "Myliobatidae", "Eleotridae", "Gobiidae", "Liparidae", "Ictaluridae", "Centriscidae", "Labridae", "Chaunacidae", "Alepocephalidae", "Triglidae", "Mormyridae", "Carangidae", "Kyphosidae", "Carcharhinidae", "Xenocyprididae", "Acanthuridae", "Siluridae", "Melamphaidae", "Apogonidae", "Clupeidae", "Blenniidae", "Aulostomidae", "Sciaenidae", "Catostomidae", "Cynoglossidae", "Monacanthidae", "Sebastidae", "Fundulidae", "Cichlidae", "Alopiidae", "Tetraodontidae", "Lutjanidae", "Lethrinidae", "Megalopidae", "Gobionidae", "Scorpaenidae", "Percichthyidae", "Arhynchobatidae", "Odontobutidae", "Pangasiidae", "Polymixiidae", "Centrarchidae", "Poeciliidae", "Cottidae", "Acheilognathidae", "Antennariidae", "Zoarcidae", "Cyclopsettidae", "Chaetodontidae", "Squatinidae", "Sisoridae", "Mugilidae", "Anarhichadidae", "Artedidraconidae", "Melanotaeniidae", "Heptapteridae", "Stomiidae", "Osteoglossidae", "Ophichthidae", "Trichiuridae", "Siganidae", "Rhinochimaeridae", "Ammodytidae", "Retropinnidae", "Peristediidae", "Scombridae", "Loricariidae", "Chlopsidae", "Cobitidae", "Notopteridae", "Channidae", "Anabantidae", "Terapontidae", "Botiidae", "Etmopteridae", "Engraulidae", "Percidae", "Pleuronectidae", "Sinipercidae", "Pristigasteridae", "Stichaeidae", "Serrasalmidae", "Torpedinidae", "Myctophidae", "Adrianichthyidae", "Tetrarogidae", "Centrolophidae", "Sparidae", "Epigonidae", "Soleidae", "Clariidae", "Halosauridae", "Pomacanthidae", "Chimaeridae", "Goodeidae", "Tripterygiidae", "Moridae", "Heterodontidae", "Osphronemidae", "Lampridae", "Belonidae", "Distichodontidae", "Leiognathidae", "Sillaginidae", "Trachichthyidae", "Evermannellidae", "Umbridae", "Bramidae", "Psilorhynchidae", "Ophidiidae", "Neoscopelidae", "Synaphobranchidae", "Rajidae", "Haemulidae", "Scyliorhinidae", "Hemiramphidae", "Danionidae", "Pimelodidae", "Ariidae", "Diplomystidae", "Auchenipteridae", "Pseudopimelodidae", "Psychrolutidae", "Congridae", "Prochilodontidae", "Aphaniidae", "Cirrhitidae", "Hexagrammidae", "Mastacembelidae", "Claroteidae", "Triacanthodidae", "Uranoscopidae", "Agonidae", "Gasterosteidae", "Bryconidae", "Stromateidae", "Labrisomidae", "Balistidae", "Platycephalidae", "Channichthyidae", "Mochokidae", "Lotidae", "Nomeidae", "Moronidae", "Cyprinodontidae", "Dasyatidae", "Salangidae", "Echeneidae", "Ailiidae", "Exocoetidae", "Nemipteridae", "Ogcocephalidae", "Cepolidae", "Gadidae", "Odontaspididae", "Hexanchidae", "Centrophoridae", "Diodontidae", "Amblycipitidae", "Gobiesocidae", "Pomacentridae", "Austroglanididae", "Gigantactinidae", "Characidae", "Caproidae", "Potamotrygonidae", "Lepisosteidae", "Synbranchidae", "Synodontidae", "Coryphaenidae", "Galaxiidae", "Trichomycteridae", "Doradidae", "Anablepidae", "Callichthyidae", "Hemigaleidae", "Datnioididae", "Balitoridae", "Badidae", "Atherinopsidae", "Callionymidae", "Schindleriidae", "Polynemidae", "Pristolepididae", "Setarchidae", "Triakidae", "Zeidae", "Mullidae", "Atherinidae", "Sphyraenidae", "Pristidae", "Hapalogenyidae", "Gerreidae", "Squalidae", "Plesiopidae", "Molidae", "Ariommatidae", "Rhombosoleidae", "Ambassidae", "Osmeridae", "Sternoptychidae", "Malacanthidae", "Ostraciidae", "Gyrinocheilidae", "Aplocheilidae", "Dalatiidae", "Scophthalmidae", "Fistulariidae", "Phycidae", "Esocidae", "Trachipteridae", "Hemiscylliidae", "Bothidae", "Paralichthyidae", "Berycidae", "Curimatidae", "Solenostomidae", "Paralepididae", "Anostomidae", "Ephippidae", "Crenuchidae", "Embiotocidae", "Pholidae", "Anoplopomatidae", "Ctenoluciidae", "Muraenesocidae", "Percophidae", "Plotosidae", "Centropomidae", "Merlucciidae", "Rivulidae", "Argentinidae", "Pseudochromidae", "Pempheridae", "Chiasmodontidae", "Psettodidae", "Somniosidae", "Anomalopidae", "Priacanthidae", "Polyodontidae", "Scopelarchidae", "Gymnotidae", "Chlorophthalmidae", "Albulidae", "Rhynchobatidae", "Pegasidae", "Microstomatidae", "Aulopidae", "Schilbidae", "Scatophagidae", "Polycentridae", "Ceratiidae", "Nandidae", "Acropomatidae", "Pentacerotidae", "Dussumieriidae", "Synanceiidae", "Sternopygidae", "Rhinobatidae", "Bythitidae", "Nettastomatidae", "Bregmacerotidae", "Pinguipedidae", "Toxotidae", "Himantolophidae", "Cetomimidae", "Valenciidae", "Oreosomatidae", "Pristiophoridae", "Glaucostegidae", "Platyrhinidae", "Gaidropsaridae", "Tanichthyidae", "Cheilodactylidae", "Muraenolepididae", "Bovichtidae", "Callorhinchidae", "Ginglymostomatidae", "Lophotidae", "Achiridae", "Symphysanodontidae", "Bathydraconidae", "Drepaneidae", "Phosichthyidae", "Aulorhynchidae", "Regalecidae", "Samaridae", "Lophiidae", "Opistognathidae", "Platytroctidae", "Ateleopodidae", "Oneirodidae", "Hoplichthyidae", "Lobotidae", "Dactyloscopidae", "Citharidae", "Caristiidae", "Notacanthidae", "Serrivomeridae", "Grammicolepididae", "Linophrynidae", "Hiodontidae", "Gonorynchidae", "Trichodontidae", "Dactylopteridae", "Elopidae", "Gonostomatidae", "Zenionidae", "Diretmidae", "Zenarchopteridae", "Opisthoproctidae", "Howellidae", "Lebiasinidae", "Aracanidae", "Caulophrynidae", "Cyematidae", "Moringuidae", "Erythrinidae", "Bathysauridae", "Scombropidae", "Malakichthyidae", "Bathylagidae", "Parazenidae", "Gasteropelecidae", "Ipnopidae", "Trichonotidae", "Trachinidae", "Batrachoididae", "Bathyclupeidae", "Nemichthyidae", "Polyprionidae", "Alestidae", "Aploactinidae", "Thaumatichthyidae", "Citharinidae", "Elassomatidae", "Narcinidae", "Parabembridae", "Emmelichthyidae", "Triacanthidae", "Ereuniidae", "Giganturidae", "Melanocetidae", "Alepisauridae", "Oplegnathidae", "Chilodontidae", "Gymnuridae", "Derichthyidae", "Lateolabracidae", "Percopsidae", "Cetopsidae", "Tetragonuridae", "Creediidae", "Apteronotidae", "Odacidae", "Kuhliidae", "Chirocentridae", "Diceratiidae"]),
           'nr_seqs': (int, 10_000), 'batch_size': (int, 500),
           'fixed_size_method': (
               str, 'pad', None,
               'Method for transforming sequences to fixed length',
               ['pad', 'window', 'repeat']),
           'rev_comp': (bool, False), 'rev_comp_mode': (
               str, 'append', None, '', ['append', 'random',
                                         'independent']),
           'enc_dimension': (int, 65),
           'enc_k': (int, 3),
           'enc_stride': (int, 3),
           'cache_batches': (bool, True),
           'cache_seq_limit': (int, None),
           'root_fa_dir':
           (str, 'sequences'),
           'root_fragments_dir':
           (str, 'fragments'),
           'file_names_cache':
           (str,
            'sequences/files.json'),
           'enc_method':
           (str, 'words2index', None, '',
            ['words2index', 'words2onehot', 'words2vec']),
           'w2vfile': (str, None, None, 'filename of a pickled word '
                       'vector dict'),
           'bert_token_dict_json':
           (str, '', None, 'path to the JSON-serialized keras-bert '
            'token dict'),
           'bert_pretrained_path':
           (str, '', None, 'path to pre-trained keras-bert model'),
           'max_seq_len': (int, 10_000, None,
                           'Length of *all* sequences when '
                           'using any `fixed_size_method`')}}
