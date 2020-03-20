from django.db import transaction
from django.contrib.auth.models import User, Group
from .models import ForceReset, Suppliers, Reagents, Internal, Validation, Recipe, Inventory, Solutions, CytoUsage

def PRIME():
    with transaction.atomic():
        User_Mod = Group.objects.create(name="User_Mod")
        perms=['13','14','16','8','5','6','9','10','12']
        for p in perms:
            User_Mod.permissions.add(p)
        Non_SU_Admin = Group.objects.create(name="Non_SU_Admin")
        perms2=['1','2','4','5','6','8','9','10','12','13','14','16','17','18','19','21','22','23','24']
        for p2 in perms2:
            Non_SU_Admin.permissions.add(p2)
        #password fine in here as after first log on required to change it
        user = User.objects.create_user("Admin", "", "password")
        user.first_name = ""
        user.last_name = ""
        user.is_superuser=True
        user.is_staff=True
        user.save()
        sups=["Abbott",
              "Agilent Technologies",
              "Applied Biosystems",
              "Beckman Coulter",
              "Bioline",
              "Bio-Rad",
              "Caltag",
              "Cambridge Bioscience ",
              "Clent Life Science",
              "DNA GenoTek",
              "Elucigene",
              "Fisher Scientific",
              "Illumina",
              "Invitrogen",
              "KapaBiosystems",
              "Launch Diagnostics",
              "LGC",
              "Life Technologies",
              "Merck Millipore",
              "Microzone",
              "MRC Holland",
              "New England BioLabs",
              "Promega",
              "Qiagen",
              "Roche",
              "Sigma Aldrich",
              "SLS (Scientific Laboratory Supplies)",
              "Sophia Genetics",
              "TaKaRa Clontech",
              "Twist Bioscience",
              "VH bio",
              "VWR"]
        for sup in sups:
            Suppliers.create(sup)
        for name, cata, sup, minimum, cyto in (('100g AGAROSE TYPE II: MEDIUM EEO~', 'A6877', 'Sigma Aldrich', '3', False),
                                                ('0.5M EDTA pH8.0~', 'AM9261', 'Life Technologies', '1', False),
                                                ('SALSA MLPA Reagents for 2000 rxns', 'EK20-FAM', 'MRC Holland', '1', False),
                                                ('200 µl S4 Sample Stabiliser - 200 reactions', 'SMR04', 'MRC Holland', '3', False),
                                                ('115 µl HhaI', 'SMR50', 'MRC Holland', '1', False),
                                                ('GeneScan™ 500 LIZ™ dye Size Standard~', '4322682', 'Life Technologies', '2', False),
                                                ('GeneScan™ 600 LIZ® dye Size Standard~', '4366589', 'Life Technologies', '1', False),
                                                ('HI-DI FORMAMIDE~', '4311320', 'Life Technologies', '2', False),
                                                ('Devyser CFTR combo CORE + UK', '8-A603', 'Launch Diagnostics', '2', False),
                                                ('AmplideX PCR/Ce FMR1 Kit - Asuragen 100 reactions', '676008', 'VH bio', '1', False),
                                                ('AmplideX® FMR1 PCR Process Control RUO - 24µl (12 reactions)', '649513', 'VH bio', '1', False),
                                                ('AmpFlSTR Identification kit', '4322288', 'Life Technologies', '1', False),
                                                ('Amplitaq Gold with buffer II and MgCl solution - 250units', 'N8080241', 'Life Technologies', '1', False),
                                                ('Pwo DNA Polymerase - 200units', '11644955001', 'Sigma Aldrich', '1', False),
                                                ('MEGAMIX BLUE', '2MMB-5', 'Clent Life Science', '1', False),
                                                ('TaKaRa LA Taq Hot-start version - 125 units', 'RR042A', 'TaKaRa Clontech', '3', False),
                                                ('TaKaRa LA Taq Hot-start version - 500 units', 'RR042B', 'TaKaRa Clontech', '1', False),
                                                ('QIAGEN Multiplex PCR Kit (1000) Each', '206145', 'Qiagen', '1', False),
                                                ('T4 DNA Ligase (1 U/µL) - 500 units', '15224025', 'Life Technologies', '1', False),
                                                ('Apa I Restriction Enzyme - 5000units', '10703753001', 'Sigma Aldrich', '1', False),
                                                ('DNA molecular weight marker II', '10236250001', 'Sigma Aldrich', '1', False),
                                                ('Bgl I Restriction Enzyme - 2000units', 'ER0071', 'Life Technologies', '1', False),
                                                ('Hpa II Restriction Enzyme', 'R0171S', 'New England BioLabs', '1', False),
                                                ('Hae III Restriction Enzyme - 3000 units', 'R0108S', 'New England BioLabs', '1', False),
                                                ('BclI Restriction Enzyme - 10,000units/ml', 'R0160S', 'New England BioLabs', '1', False),
                                                ('RsaI Restriction Enzyme - 5000rxns', 'R0167L', 'New England BioLabs', '1', False),
                                                ('MboI Restriction Enzyme - 2500rxns', 'R0147L', 'New England BioLabs', '1', False),
                                                ('Hi-Strength Analytical Agarose', 'H15669', 'SLS (Scientific Laboratory Supplies)', '1', False),
                                                ('PfuUltra II Fusion HotStart DNA Polymerase, 40 rxn Each', '600670', 'Qiagen', '1', False),
                                                ('Taq DNA Polymerase, 5 U/µl', '11146173001', 'Sigma Aldrich', '1', False),
                                                ("O'rangeruler 100bp ladder - 25µg", 'SM0623', 'Life Technologies', '1', False),
                                                ('Quick-Load® Purple 50 bp DNA Ladder - 250 reactions', 'N0556S', 'New England BioLabs', '1', False),
                                                ('HindIII Restriction enzyme - 20,000 units/ml', 'R0104S', 'New England BioLabs', '1', False),
                                                ('TAQMAN GENE EXPRESSION MASTER MIX', '4369016', 'Life Technologies', '1', False),
                                                ('PyroMark Gold Q96 Reagents (5 x 96)', '972804', 'Qiagen', '1', False),
                                                ('PyroMark Denaturation Sol. (500 ml)', '979007', 'Qiagen', '2', False),
                                                ('PyroMark Wash Buffer (conc., 200 ml)', '979008', 'Qiagen', '1', False),
                                                ('PyroMark Annealing Buffer (250 ml)', '979009', 'Qiagen', '1', False),
                                                ('STREPTAVIDIN SEPHAROSE HIGH PERFORMANCE', '17-5113-01', 'VWR', '1', False),
                                                ('MEGAMIX ROYAL - 50ml', '2MMR-50', 'Clent Life Science', '1', False),
                                                ):
            
            values={}
            values["name"]=name
            values["cat_no"]=cata
            values["supplier_def"]=Suppliers.objects.get(name=sup)
            values["min_count"]=int(minimum)
            values["is_cyto"]=cyto
            Reagents.create(values)
