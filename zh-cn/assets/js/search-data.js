
const currentUrl = window.location.href;
const siteUrl = "https://lyz20051019.github.io"; 
let updatedUrl = currentUrl.replace("https://lyz20051019.github.io", "");
if (currentUrl.length == updatedUrl.length && currentUrl.startsWith("http://127.0.0.1")) {
  const otherSiteUrl = siteUrl.replace("localhost", "127.0.0.1");
  updatedUrl = currentUrl.replace(otherSiteUrl + "", "");
}
if ("zh-cn".length > 0) {
  updatedUrl = updatedUrl.replace("/zh-cn", "");
}
// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-简介",
    title: "简介",
    section: "导航菜单",
    handler: () => {
      window.location.href = "/zh-cn/";
    },
  },{id: "nav-新闻",
          title: "新闻",
          description: "",
          section: "导航菜单",
          handler: () => {
            window.location.href = "/zh-cn/news/";
          },
        },{id: "nav-出版物",
          title: "出版物",
          description: "按类别分类的出版物，按时间顺序排列（由 jekyll-scholar 生成）",
          section: "导航菜单",
          handler: () => {
            window.location.href = "/zh-cn/publications/";
          },
        },{id: "nav-仓库",
          title: "仓库",
          description: "",
          section: "导航菜单",
          handler: () => {
            window.location.href = "/zh-cn/repositories/";
          },
        },{id: "nav-简历",
          title: "简历",
          description: "",
          section: "导航菜单",
          handler: () => {
            window.location.href = "/zh-cn/cv/";
          },
        },{id: "nav-成员",
          title: "成员",
          description: "课题组成员",
          section: "导航菜单",
          handler: () => {
            window.location.href = "/zh-cn/people/";
          },
        },{id: "nav-活动",
          title: "活动",
          description: "",
          section: "导航菜单",
          handler: () => {
            window.location.href = "/zh-cn/events/";
          },
        },{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "",handler: () => {
              window.location.href = "/zh-cn/books/zh-cn/the_godfather.html";
            },},{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "",handler: () => {
              window.location.href = "/zh-cn/books/pt-br/the_godfather.html";
            },},{id: "events-课题组合照",
          title: '课题组合照',
          description: "课题组合照",
          section: "",handler: () => {
              window.location.href = "/zh-cn/events/events1/";
            },},{id: "news-祝贺课题组成员在-未知期刊-上发表了论文-data-driven-phosphine-ligand-design-of-ni-catalyzed-enantioselective-suzuki-miyaura-cross-coupling-reaction-for-the-synthesis-of-biaryl-atropisomers-standing-on-the-shoulder-of-pd-catalysis-giants",
          title: '祝贺课题组成员在《未知期刊》上发表了论文《Data-Driven Phosphine Ligand Design of Ni-Catalyzed Enantioselective Suzuki–Miyaura Cross-Coupling Reaction for the Synthesis...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.26434_chemrxiv-2024-03v52.html";
            },},{id: "news-祝贺课题组成员在-chemical-science-上发表了论文-nickel-catalyzed-amination-of-aryl-carbamates-and-sequential-site-selective-cross-couplings",
          title: '祝贺课题组成员在《Chemical Science》上发表了论文《Nickel-catalyzed amination of aryl carbamates and sequential site-selective cross-couplings》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1039_c1sc00230a.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-origins-of-ligand-controlled-selectivities-in-ni-nhc-catalyzed-intramolecular-5-2-cycloadditions-and-homo-ene-reactions-a-theoretical-study",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Mechanism and Origins of Ligand-Controlled Selectivities in [Ni(NHC)]-Catalyzed...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja309873z.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-origins-of-selectivity-in-ru-ii-catalyzed-intramolecular-5-2-cycloadditions-and-ene-reactions-of-vinylcyclopropanes-and-alkynes-from-density-functional-theory",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Mechanism and Origins of Selectivity in Ru(II)-Catalyzed Intramolecular...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja4012657.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-mechanisms-and-origins-of-switchable-chemoselectivity-of-ni-catalyzed-c-aryl-o-and-c-acyl-o-activation-of-aryl-esters-with-phosphine-ligands",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Mechanisms and Origins of Switchable Chemoselectivity of Ni-Catalyzed...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja4118413.html";
            },},{id: "news-祝贺课题组成员在-organic-letters-上发表了论文-how-tethers-control-the-chemo-and-regioselectivities-of-intramolecular-cycloadditions-between-aryl-1-aza-2-azoniaallenes-and-alkenes",
          title: '祝贺课题组成员在《Organic Letters》上发表了论文《How Tethers Control the Chemo- and Regioselectivities of Intramolecular Cycloadditions between Aryl-1-aza-2-azoniaallenes...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ol501958s.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-selectivity-of-n-triflylphosphoramide-catalyzed-3-2-cycloaddition-between-hydrazones-and-alkenes",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Mechanism and Selectivity of N-Triflylphosphoramide Catalyzed (3(+)+2) Cycloaddition...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja506660c.html";
            },},{id: "news-祝贺课题组成员在-organic-letters-上发表了论文-why-alkynyl-substituents-dramatically-accelerate-hexadehydro-diels-alder-hdda-reactions-stepwise-mechanisms-of-hdda-cycloadditions",
          title: '祝贺课题组成员在《Organic Letters》上发表了论文《Why Alkynyl Substituents Dramatically Accelerate Hexadehydro-Diels-Alder (HDDA) Reactions: Stepwise Mechanisms of HDDA...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ol502780w.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-reactivity-and-chemoselectivity-of-allenes-in-rh-i-catalyzed-intermolecular-5-2-cycloadditions-with-vinylcyclopropanes-allene-mediated-rhodacycle-formation-can-poison-rh-i-catalyzed-cycloadditions",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Reactivity and Chemoselectivity of Allenes in Rh(I)-Catalyzed Intermolecular...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja5098308.html";
            },},{id: "news-祝贺课题组成员在-the-journal-of-organic-chemistry-上发表了论文-mechanism-reactivity-and-selectivity-of-nickel-catalyzed-4-4-2-cycloadditions-of-dienes-and-alkynes",
          title: '祝贺课题组成员在《The Journal of Organic Chemistry》上发表了论文《Mechanism, Reactivity, and Selectivity of Nickel-Catalyzed [4+4+2] Cycloadditions of...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jo502219d.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-ni-nhc-catalyzed-cycloaddition-of-diynes-and-tropone-apparent-enone-cycloaddition-involving-an-8-pi-insertion",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Ni(NHC)]-Catalyzed Cycloaddition of Diynes and Tropone: Apparent Enone...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja5105206.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-iodoarene-catalyzed-stereospecific-intramolecular-sp-3-c-h-amination-reaction-development-and-mechanistic-insights",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Iodoarene-Catalyzed Stereospecific Intramolecular sp(3) C-H Amination: Reaction Development...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5b03488.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-dynamics-of-intramolecular-c-h-insertion-reactions-of-1-aza-2-azoniaallene-salts",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Mechanism and Dynamics of Intramolecular C-H Insertion Reactions...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5b04474.html";
            },},{id: "news-祝贺课题组成员在-nature-上发表了论文-conversion-of-amides-to-esters-by-the-nickel-catalysed-activation-of-amide-c-n-bonds",
          title: '祝贺课题组成员在《Nature》上发表了论文《Conversion of amides to esters by the nickel-catalysed activation of amide C-N bonds》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_nature14615.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-computational-exploration-of-mechanism-and-selectivities-of-nhc-nickel-ii-hydride-catalyzed-hydroalkenylations-of-styrene-with-alpha-olefins",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《Computational Exploration of Mechanism and Selectivities of (NHC)Nickel(II)hydride-Catalyzed Hydroalkenylations of Styrene with...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.5b01075.html";
            },},{id: "news-祝贺课题组成员在-acs-central-science-上发表了论文-mechanistic-insights-into-two-phase-radical-c-h-arylations",
          title: '祝贺课题组成员在《ACS Central Science》上发表了论文《Mechanistic Insights into Two-Phase Radical C-H Arylations》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscentsci.5b00332.html";
            },},{id: "news-祝贺课题组成员在-organic-letters-上发表了论文-ligand-controlled-diastereoselective-1-3-dipolar-cycloadditions-of-azomethine-ylides-with-methacrylonitrile",
          title: '祝贺课题组成员在《Organic Letters》上发表了论文《Ligand-Controlled Diastereoselective 1,3-Dipolar Cycloadditions of Azomethine Ylides with Methacrylonitrile》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.orglett.5b03171.html";
            },},{id: "news-祝贺课题组成员在-angewandte-chemie-international-edition-上发表了论文-nickel-catalyzed-activation-of-acyl-c-o-bonds-of-methyl-esters",
          title: '祝贺课题组成员在《Angewandte Chemie International Edition》上发表了论文《Nickel-Catalyzed Activation of Acyl C-O Bonds of Methyl Esters》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.201511486.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-how-doped-mos2-breaks-transition-metal-scaling-relations-for-co2-electrochemical-reduction",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《How Doped MoS2 Breaks Transition-Metal Scaling Relations for CO2 Electrochemical Reduction》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.6b00619.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-distortion-controlled-reactivity-and-molecular-dynamics-of-dehydro-diels-alder-reactions",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Distortion-Controlled Reactivity and Molecular Dynamics of Dehydro-Diels-Alder Reactions》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.6b04113.html";
            },},{id: "news-祝贺课题组成员在-science-上发表了论文-ligand-accelerated-enantioselective-methylene-c-sp-3-h-bond-activation",
          title: '祝贺课题组成员在《Science》上发表了论文《Ligand-accelerated enantioselective methylene C(sp(3))-H bond activation》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1126_science.aaf4434.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-palladium-catalyzed-suzuki-miyaura-coupling-of-aryl-esters",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Palladium-Catalyzed Suzuki-Miyaura Coupling of Aryl Esters》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.6b12329.html";
            },},{id: "news-祝贺课题组成员在-the-journal-of-organic-chemistry-上发表了论文-2-1-cycloaddition-reactions-give-further-evidence-of-the-nitrenium-like-character-of-1-aza-2-azoniaallene-salts",
          title: '祝贺课题组成员在《The Journal of Organic Chemistry》上发表了论文《(2+1)-Cycloaddition Reactions Give Further Evidence of the Nitrenium-like Character...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.joc.7b00407.html";
            },},{id: "news-祝贺课题组成员在-nature-communications-上发表了论文-understanding-trends-in-electrochemical-carbon-dioxide-reduction-rates",
          title: '祝贺课题组成员在《Nature Communications》上发表了论文《Understanding trends in electrochemical carbon dioxide reduction rates》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_ncomms15438.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-mechanisms-and-origins-of-chemo-and-regioselectivities-of-ru-ii-catalyzed-decarboxylative-c-h-alkenylation-of-aryl-carboxylic-acids-with-alkynes-a-computational-study",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Mechanisms and Origins of Chemo- and Regioselectivities of...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.7b00714.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-the-origins-of-dramatic-differences-in-five-membered-vs-six-membered-chelation-of-pd-ii-on-efficiency-of-c-sp-3-h-bond-activation",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《The Origins of Dramatic Differences in Five-Membered vs...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.7b01801.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-n-heterocyclic-carbene-cu-catalyzed-enantioselective-conjugate-additions-with-alkenylboronic-esters-as-nucleophiles",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《N-heterocyclic Carbene–Cu-Catalyzed Enantioselective Conjugate Additions with Alkenylboronic Esters as Nucleophiles》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.7b02132.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-origins-of-ligand-controlled-stereoselectivity-of-ni-catalyzed-suzuki-miyaura-coupling-with-benzylic-esters-a-computational-study",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Mechanism and Origins of Ligand-controlled Stereoselectivity of Ni-Catalyzed...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.7b04973.html";
            },},{id: "news-祝贺课题组成员在-science-china-chemistry-上发表了论文-ni-mediated-c-n-activation-of-amides-and-derived-catalytic-transformations",
          title: '祝贺课题组成员在《Science China Chemistry》上发表了论文《Ni-mediated C–N activation of amides and derived catalytic transformations》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1007_s11426-017-9025-1.html";
            },},{id: "news-祝贺课题组成员在-asian-journal-of-organic-chemistry-上发表了论文-copper-catalyzed-enantioselective-hydroboration-of-1-1-disubstituted-alkenes-method-development-applications-and-mechanistic-studies",
          title: '祝贺课题组成员在《Asian Journal of Organic Chemistry》上发表了论文《Copper-Catalyzed Enantioselective Hydroboration of 1,1-Disubstituted Alkenes: Method Development, Applications...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_ajoc.201700503.html";
            },},{id: "news-祝贺课题组成员在-angewandte-chemie-international-edition-上发表了论文-copper-catalyzed-enantioselective-markovnikov-protoboration-of-α-olefins-enabled-by-a-buttressed-n-heterocyclic-carbene-ligand",
          title: '祝贺课题组成员在《Angewandte Chemie International Edition》上发表了论文《Copper-Catalyzed Enantioselective Markovnikov Protoboration of α-Olefins Enabled by a Buttressed...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.201711229.html";
            },},{id: "news-祝贺课题组成员在-organometallics-上发表了论文-mechanism-and-origins-of-chemo-and-regioselectivities-of-pd-catalyzed-intermolecular-σ-bond-exchange-between-benzocyclobutenones-and-silacyclobutanes-a-computational-study",
          title: '祝贺课题组成员在《Organometallics》上发表了论文《Mechanism and Origins of Chemo- and Regioselectivities of Pd-Catalyzed Intermolecular σ-Bond Exchange between...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.organomet.7b00903.html";
            },},{id: "news-祝贺课题组成员在-nature-communications-上发表了论文-coulombic-enhanced-hetero-radical-pairing-interactions",
          title: '祝贺课题组成员在《Nature Communications》上发表了论文《Coulombic-enhanced hetero radical pairing interactions》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41467-018-04335-0.html";
            },},{id: "news-祝贺课题组成员在-the-journal-of-organic-chemistry-上发表了论文-rhodium-catalyzed-asymmetric-addition-of-organoboronic-acids-to-aldimines-using-chiral-spiro-monophosphite-olefin-ligands-method-development-and-mechanistic-studies",
          title: '祝贺课题组成员在《The Journal of Organic Chemistry》上发表了论文《Rhodium-Catalyzed Asymmetric Addition of Organoboronic Acids to Aldimines Using...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.joc.8b01764.html";
            },},{id: "news-祝贺课题组成员在-communications-chemistry-上发表了论文-catalytic-asymmetric-synthesis-of-chiral-trisubstituted-heteroaromatic-allenes-from-1-3-enynes",
          title: '祝贺课题组成员在《Communications Chemistry》上发表了论文《Catalytic asymmetric synthesis of chiral trisubstituted heteroaromatic allenes from 1,3-enynes》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s42004-018-0065-4.html";
            },},{id: "news-祝贺课题组成员在-molecules-上发表了论文-computational-study-of-mechanism-and-thermodynamics-of-ni-ipr-catalyzed-amidation-of-esters",
          title: '祝贺课题组成员在《Molecules》上发表了论文《Computational Study of Mechanism and Thermodynamics of Ni/IPr-Catalyzed Amidation of Esters》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.3390_molecules23102681.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-palladium-catalyzed-selective-five-fold-cascade-arylation-of-the-12-vertex-monocarborane-anion-by-b-h-activation",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Palladium-Catalyzed Selective Five-Fold Cascade Arylation of the 12-Vertex...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.8b07872.html";
            },},{id: "news-祝贺课题组成员在-organic-letters-上发表了论文-n-heterocyclic-carbene-cu-catalyzed-enantioselective-allenyl-conjugate-addition",
          title: '祝贺课题组成员在《Organic Letters》上发表了论文《N-Heterocyclic Carbene–Cu-Catalyzed Enantioselective Allenyl Conjugate Addition》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.orglett.8b03029.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-alternate-heme-ligation-steers-activity-and-selectivity-in-engineered-cytochrome-p450-catalyzed-carbene-transfer-reactions",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Alternate Heme Ligation Steers Activity and Selectivity in...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.8b09613.html";
            },},{id: "news-祝贺课题组成员在-organometallics-上发表了论文-stepwise-versus-concerted-reductive-elimination-mechanisms-in-the-carbon-iodide-bond-formation-of-dpephos-rhmei2-complex",
          title: '祝贺课题组成员在《Organometallics》上发表了论文《Stepwise versus Concerted Reductive Elimination Mechanisms in the Carbon–Iodide Bond Formation of (DPEphos)RhMeI2...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.organomet.8b00723.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-stereoretentive-c-sp3-s-cross-coupling",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Stereoretentive C(sp3)–S Cross-Coupling》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.8b11211.html";
            },},{id: "news-祝贺课题组成员在-chinese-journal-of-chemistry-上发表了论文-enantioselective-intramolecular-desymmetric-α-addition-of-cyclohexanone-to-propiolamide-catalyzed-by-sodium-l-prolinate",
          title: '祝贺课题组成员在《Chinese Journal of Chemistry》上发表了论文《Enantioselective Intramolecular Desymmetric α-Addition of Cyclohexanone to Propiolamide Catalyzed by...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_cjoc.201800420.html";
            },},{id: "news-祝贺课题组成员在-synlett-上发表了论文-engineered-cytochrome-c-catalyzed-lactone-carbene-b-h-insertion",
          title: '祝贺课题组成员在《Synlett》上发表了论文《Engineered Cytochrome c-Catalyzed Lactone-Carbene B–H Insertion》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1055_s-0037-1611662.html";
            },},{id: "news-祝贺课题组成员在-acs-energy-letters-上发表了论文-tuning-the-lumo-energy-of-an-organic-interphase-to-stabilize-lithium-metal-batteries",
          title: '祝贺课题组成员在《ACS Energy Letters》上发表了论文《Tuning the LUMO Energy of an Organic Interphase to Stabilize Lithium...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acsenergylett.8b02483.html";
            },},{id: "news-祝贺课题组成员在-organic-letters-上发表了论文-c-h-acidity-and-arene-nucleophilicity-as-orthogonal-control-of-chemoselectivity-in-dual-c-h-bond-activation",
          title: '祝贺课题组成员在《Organic Letters》上发表了论文《C–H Acidity and Arene Nucleophilicity as Orthogonal Control of Chemoselectivity in Dual...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.orglett.9b00633.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-nucleophile-dependent-z-e-and-regioselectivity-in-the-palladium-catalyzed-asymmetric-allylic-c-h-alkylation-of-1-4-dienes",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Nucleophile-Dependent Z/E- and Regioselectivity in the Palladium-Catalyzed Asymmetric...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.8b13582.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-a-unified-explanation-for-chemoselectivity-and-stereospecificity-of-ni-catalyzed-kumada-and-cross-electrophile-coupling-reactions-of-benzylic-ethers-a-combined-computational-and-experimental-study",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《A Unified Explanation for Chemoselectivity and Stereospecificity of...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.9b00097.html";
            },},{id: "news-祝贺课题组成员在-organometallics-上发表了论文-unexpected-stability-of-co-coordinated-palladacycle-in-bidentate-auxiliary-directed-c-sp3-h-bond-activation-a-combined-experimental-and-computational-study",
          title: '祝贺课题组成员在《Organometallics》上发表了论文《Unexpected Stability of CO-Coordinated Palladacycle in Bidentate Auxiliary Directed C(sp3)–H Bond Activation: A...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.organomet.9b00087.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-rhodium-iii-catalyzed-asymmetric-borylative-cyclization-of-cyclohexadienone-containing-1-6-dienes-an-experimental-and-dft-study",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Rhodium(III)-Catalyzed Asymmetric Borylative Cyclization of Cyclohexadienone-Containing 1,6-Dienes: An...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.9b05583.html";
            },},{id: "news-祝贺课题组成员在-organic-process-research-amp-amp-development-上发表了论文-aluminum-catalyzed-selective-hydroboration-of-alkenes-and-alkynylsilanes",
          title: '祝贺课题组成员在《Organic Process Research &amp;amp;amp; Development》上发表了论文《Aluminum-Catalyzed Selective Hydroboration of Alkenes and Alkynylsilanes》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.oprd.9b00205.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-how-solvents-control-the-stereospecificity-of-ni-catalyzed-miyaura-borylation-of-allylic-pivalates",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《How Solvents Control the Stereospecificity of Ni-Catalyzed Miyaura Borylation of Allylic Pivalates》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.9b02636.html";
            },},{id: "news-祝贺课题组成员在-organic-letters-上发表了论文-computation-guided-development-of-the-click-ortho-quinone-methide-cycloaddition-with-improved-kinetics",
          title: '祝贺课题组成员在《Organic Letters》上发表了论文《Computation-Guided Development of the “Click” ortho-Quinone Methide Cycloaddition with Improved Kinetics》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.orglett.0c00578.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-catalytic-and-photochemical-strategies-to-stabilized-radicals-based-on-anomeric-nucleophiles",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Catalytic and Photochemical Strategies to Stabilized Radicals Based...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.0c03298.html";
            },},{id: "news-祝贺课题组成员在-angewandte-chemie-international-edition-上发表了论文-predicting-regioselectivity-in-radical-c-h-functionalization-of-heterocycles-through-machine-learning",
          title: '祝贺课题组成员在《Angewandte Chemie International Edition》上发表了论文《Predicting Regioselectivity in Radical C−H Functionalization of Heterocycles through Machine...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.202000959.html";
            },},{id: "news-祝贺课题组成员在-accounts-of-chemical-research-上发表了论文-mechanism-and-selectivity-control-in-ni-and-pd-catalyzed-cross-couplings-involving-carbon-oxygen-bond-activation",
          title: '祝贺课题组成员在《Accounts of Chemical Research》上发表了论文《Mechanism and Selectivity Control in Ni- and Pd-Catalyzed Cross-Couplings Involving...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.accounts.1c00050.html";
            },},{id: "news-祝贺课题组成员在-angewandte-chemie-international-edition-上发表了论文-towards-data-driven-design-of-asymmetric-hydrogenation-of-olefins-database-and-hierarchical-learning",
          title: '祝贺课题组成员在《Angewandte Chemie International Edition》上发表了论文《Towards Data‐Driven Design of Asymmetric Hydrogenation of Olefins: Database and...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.202106880.html";
            },},{id: "news-祝贺课题组成员在-synlett-上发表了论文-a-molecular-stereostructure-descriptor-based-on-spherical-projection",
          title: '祝贺课题组成员在《Synlett》上发表了论文《A Molecular Stereostructure Descriptor Based On Spherical Projection》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1055_s-0040-1705977.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-nickel-catalyzed-domino-cross-electrophile-coupling-dicarbofunctionalization-reaction-to-afford-vinylcyclopropanes",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《Nickel-Catalyzed Domino Cross-Electrophile Coupling Dicarbofunctionalization Reaction To Afford Vinylcyclopropanes》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.1c04235.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-n-bu-4nbr-promoted-n2-splitting-to-molybdenum-nitride",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《(n-Bu)4NBr-Promoted N2 Splitting to Molybdenum Nitride》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.2c01507.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-syntheses-of-bufospirostenin-a-and-ophiopogonol-a-by-a-conformation-controlled-transannular-prins-cyclization",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Syntheses of Bufospirostenin A and Ophiopogonol A by...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.2c07944.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-identification-of-alkoxy-radicals-as-hydrogen-atom-transfer-agents-in-ce-catalyzed-c-h-functionalization",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Identification of Alkoxy Radicals as Hydrogen Atom Transfer...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.2c10126.html";
            },},{id: "news-祝贺课题组成员在-chemistry-a-european-journal-上发表了论文-bridging-chemical-knowledge-and-machine-learning-for-performance-prediction-of-organic-synthesis",
          title: '祝贺课题组成员在《Chemistry – A European Journal》上发表了论文《Bridging Chemical Knowledge and Machine Learning for Performance Prediction...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_chem.202202834.html";
            },},{id: "news-祝贺课题组成员在-chemistry-a-european-journal-上发表了论文-frontispiece-bridging-chemical-knowledge-and-machine-learning-for-performance-prediction-of-organic-synthesis",
          title: '祝贺课题组成员在《Chemistry – A European Journal》上发表了论文《Frontispiece: Bridging Chemical Knowledge and Machine Learning for Performance...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_chem.202380662.html";
            },},{id: "news-祝贺课题组成员在-nature-synthesis-上发表了论文-enantioselectivity-prediction-of-pallada-electrocatalysed-c-h-activation-using-transition-state-knowledge-in-machine-learning",
          title: '祝贺课题组成员在《Nature Synthesis》上发表了论文《Enantioselectivity prediction of pallada-electrocatalysed C–H activation using transition state knowledge in machine...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s44160-022-00233-y.html";
            },},{id: "news-祝贺课题组成员在-science-advances-上发表了论文-brønsted-acid-catalyzed-asymmetric-dearomatization-for-synthesis-of-chiral-fused-polycyclic-enone-and-indoline-scaffolds",
          title: '祝贺课题组成员在《Science Advances》上发表了论文《Brønsted acid–catalyzed asymmetric dearomatization for synthesis of chiral fused polycyclic enone and...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1126_sciadv.adg4648.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-direct-incorporation-of-dinitrogen-into-an-aliphatic-c-h-bond",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Direct Incorporation of Dinitrogen into an Aliphatic C–H...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.2c13086.html";
            },},{id: "news-祝贺课题组成员在-chemistry-an-asian-journal-上发表了论文-exploring-spectrum-based-molecular-descriptors-for-reaction-performance-prediction",
          title: '祝贺课题组成员在《Chemistry – An Asian Journal》上发表了论文《Exploring Spectrum‐based Molecular Descriptors for Reaction Performance Prediction》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_asia.202300011.html";
            },},{id: "news-祝贺课题组成员在-nature-synthesis-上发表了论文-intermolecular-trans-bis-silylation-of-terminal-alkynes",
          title: '祝贺课题组成员在《Nature Synthesis》上发表了论文《Intermolecular trans-bis-silylation of terminal alkynes》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s44160-023-00325-3.html";
            },},{id: "news-祝贺课题组成员在-nature-communications-上发表了论文-data-driven-design-of-new-chiral-carboxylic-acid-for-construction-of-indoles-with-c-central-and-c-n-axial-chirality-via-cobalt-catalysis",
          title: '祝贺课题组成员在《Nature Communications》上发表了论文《Data-driven design of new chiral carboxylic acid for construction of indoles with...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41467-023-38872-0.html";
            },},{id: "news-祝贺课题组成员在-nature-communications-上发表了论文-reaction-performance-prediction-with-an-extrapolative-and-interpretable-graph-model-based-on-chemical-knowledge",
          title: '祝贺课题组成员在《Nature Communications》上发表了论文《Reaction performance prediction with an extrapolative and interpretable graph model based on...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41467-023-39283-x.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-enantioselective-desymmetrizing-hydroalkoxylation-of-1-4-and-1-8-diynes-enabled-by-chiral-brønsted-acid-catalysis",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《Enantioselective Desymmetrizing Hydroalkoxylation of 1,4- and 1,8-Diynes Enabled by Chiral Brønsted Acid...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.3c01680.html";
            },},{id: "news-祝贺课题组成员在-chemistry-an-asian-journal-上发表了论文-an-asynchronous-concerted-mechanism-and-its-origin-in-lewis-acid-mediated-carbonyl-olefin-2-2-cycloaddition",
          title: '祝贺课题组成员在《Chemistry – An Asian Journal》上发表了论文《An Asynchronous Concerted Mechanism and Its Origin in Lewis...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_asia.202300375.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-visible-light-mediated-energy-transfer-enables-cyclopropanes-bearing-contiguous-all-carbon-quaternary-centers",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《Visible-Light-Mediated Energy Transfer Enables Cyclopropanes Bearing Contiguous All-Carbon Quaternary Centers》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.3c02350.html";
            },},{id: "news-祝贺课题组成员在-the-journal-of-physical-chemistry-a-上发表了论文-benchmark-study-of-density-functional-theory-methods-in-geometry-optimization-of-transition-metal-dinitrogen-complexes",
          title: '祝贺课题组成员在《The Journal of Physical Chemistry A》上发表了论文《Benchmark Study of Density Functional Theory Methods in...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.jpca.3c04215.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-recent-advances-in-theoretical-studies-on-cu-mediated-bond-formation-mechanisms-involving-radicals",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《Recent Advances in Theoretical Studies on Cu-Mediated Bond Formation Mechanisms Involving Radicals》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.3c06042.html";
            },},{id: "news-祝贺课题组成员在-chinese-science-bulletin-上发表了论文-数据驱动的有机分子理化性质预测",
          title: '祝贺课题组成员在《Chinese Science Bulletin》上发表了论文《数据驱动的有机分子理化性质预测》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1360_tb-2024-0812.html";
            },},{id: "news-祝贺课题组成员在-scientific-data-上发表了论文-qm9star-two-million-dft-computed-equilibrium-structures-for-ions-and-radicals-with-atomic-information",
          title: '祝贺课题组成员在《Scientific Data》上发表了论文《QM9star, two Million DFT-computed Equilibrium Structures for Ions and Radicals with Atomic...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41597-024-03933-6.html";
            },},{id: "news-祝贺课题组成员在-nature-communications-上发表了论文-asymmetric-büchner-reaction-and-arene-cyclopropanation-via-copper-catalyzed-controllable-cyclization-of-diynes",
          title: '祝贺课题组成员在《Nature Communications》上发表了论文《Asymmetric Büchner reaction and arene cyclopropanation via copper-catalyzed controllable cyclization of diynes》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41467-024-53605-7.html";
            },},{id: "news-祝贺课题组成员在-chemistry-a-european-journal-上发表了论文-post-transition-state-bifurcation-controls-torsional-selectivity-in-radical-addition-of-allenes",
          title: '祝贺课题组成员在《Chemistry – A European Journal》上发表了论文《Post‐Transition State Bifurcation Controls Torsional Selectivity in Radical Addition...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_chem.202403316.html";
            },},{id: "news-祝贺课题组成员在-science-advances-上发表了论文-rhodium-catalyzed-atropodivergent-hydroamination-of-alkynes-by-leveraging-two-potential-enantiodetermining-steps",
          title: '祝贺课题组成员在《Science Advances》上发表了论文《Rhodium-Catalyzed Atropodivergent Hydroamination of Alkynes by Leveraging Two Potential Enantiodetermining Steps》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1126_sciadv.adr4435.html";
            },},{id: "news-祝贺课题组成员在-science-china-chemistry-上发表了论文-tandem-asymmetric-dearomatized-functionalization-reaction-of-phenols-with-evans-ynamides-enabled-by-divergent-electrophiles",
          title: '祝贺课题组成员在《Science China Chemistry》上发表了论文《Tandem asymmetric dearomatized functionalization reaction of phenols with Evans-ynamides enabled by...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1007_s11426-024-2211-y.html";
            },},{id: "news-祝贺课题组成员在-angewandte-chemie-international-edition-上发表了论文-enantioselective-synthesis-of-axially-chiral-tetrasubstituted-alkenes-by-copper-catalyzed-c-sp2-h-functionalization-of-arenes-with-vinyl-cations",
          title: '祝贺课题组成员在《Angewandte Chemie International Edition》上发表了论文《Enantioselective Synthesis of Axially Chiral Tetrasubstituted Alkenes by Copper‐Catalyzed C(sp2)–H...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.202418254.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-chiral-phosphoric-acid-catalyzed-kinetic-resolution-of-tertiary-alcohol-tethered-ynamides-via-controllable-hydroalkoxylation",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《Chiral Phosphoric Acid-Catalyzed Kinetic Resolution of Tertiary Alcohol-Tethered Ynamides via Controllable Hydroalkoxylation》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.4c08055.html";
            },},{id: "news-祝贺课题组成员在-acs-catalysis-上发表了论文-noninnocent-spectator-ligands-facilitate-co-ligand-stabilized-mn-i-metal-catalyzed-hydrogenation-of-urea-derivatives-or-carbamates-to-the-more-reactive-formamides",
          title: '祝贺课题组成员在《ACS Catalysis》上发表了论文《Noninnocent Spectator Ligands Facilitate CO Ligand-Stabilized Mn(I) Metal-Catalyzed Hydrogenation of Urea Derivatives...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.5c01249.html";
            },},{id: "news-祝贺课题组成员在-science-上发表了论文-asymmetric-amination-of-alkyl-radicals-with-two-minimally-different-alkyl-substituents",
          title: '祝贺课题组成员在《Science》上发表了论文《Asymmetric amination of alkyl radicals with two minimally different alkyl substituents》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1126_science.adu3996.html";
            },},{id: "news-祝贺课题组成员在-nature-communications-上发表了论文-ligand-controlled-divergent-asymmetric-c-sp3-h-and-c-sp3-o-insertion-via-vinyl-cations",
          title: '祝贺课题组成员在《Nature Communications》上发表了论文《Ligand-controlled divergent asymmetric C(sp3)−H and C(sp3)−O insertion via vinyl cations》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41467-025-59328-7.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-transfer-learning-enabled-ligand-prediction-for-ni-catalyzed-atroposelective-suzuki-miyaura-cross-coupling-based-on-mechanistic-similarity-leveraging-pd-knowledge-for-ni-discovery",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Transfer Learning-Enabled Ligand Prediction for Ni-Catalyzed Atroposelective Suzuki–Miyaura...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5c00838.html";
            },},{id: "news-祝贺课题组成员在-ccs-chemistry-上发表了论文-mechanism-and-origins-of-weak-bonding-controlled-selectivities-in-cinchoninium-catalyzed-umpolung-michael-addition-of-imines",
          title: '祝贺课题组成员在《CCS Chemistry》上发表了论文《Mechanism and Origins of Weak Bonding-Controlled Selectivities in Cinchoninium-Catalyzed Umpolung Michael Addition...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.31635_ccschem.024.202404401.html";
            },},{id: "news-祝贺课题组成员在-green-synthesis-and-catalysis-上发表了论文-metal-free-and-visible-light-mediated-method-enables-the-synthesis-of-olefins-from-ketones",
          title: '祝贺课题组成员在《Green Synthesis and Catalysis》上发表了论文《Metal-free and visible-light-mediated method enables the synthesis of olefins from...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1016_j.gresc.2024.02.001.html";
            },},{id: "news-祝贺课题组成员在-angewandte-chemie-international-edition-上发表了论文-copper-catalyzed-asymmetric-2-2-2-cycloaddition-of-diynes-via-vinyl-cations",
          title: '祝贺课题组成员在《Angewandte Chemie International Edition》上发表了论文《Copper‐Catalyzed Asymmetric [2 + 2 + 2] Cycloaddition of Diynes...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.202514641.html";
            },},{id: "news-祝贺课题组成员在-inorganics-上发表了论文-theoretical-study-on-the-ortho-para-reactivity-difference-in-ru-catalyzed-amination-of-aminopyridines-via-η6-coordination-role-of-meisenheimer-intermediate-coordination-ability",
          title: '祝贺课题组成员在《Inorganics》上发表了论文《Theoretical Study on the Ortho–Para Reactivity Difference in Ru-Catalyzed Amination of Aminopyridines via...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.3390_inorganics13100316.html";
            },},{id: "news-祝贺课题组成员在-chemistry-an-asian-journal-上发表了论文-computational-study-on-a-copper-catalyzed-atroposelective-dehydro-diels-alder-reaction-of-ynamide-via-vinyl-cation-mechanistic-investigations-and-chiral-induction-model",
          title: '祝贺课题组成员在《Chemistry – An Asian Journal》上发表了论文《Computational Study on a Copper‐Catalyzed Atroposelective Dehydro‐Diels–Alder Reaction of...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_asia.70282.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-highly-regio-and-enantioselective-synthesis-of-4-substituted-dihydroisoquinolones-catalyzed-by-a-planar-chiral-rhodium-iii-catalyst-bearing-a-penta-substituted-prochiral-cyclopentadienyl-ligand",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Highly Regio- and Enantioselective Synthesis of 4-Substituted Dihydroisoquinolones...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5c16993.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-construction-of-all-aliphatic-stereocenters-via-enantioselective-alkene-hydroalkylation",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Construction of All-Aliphatic Stereocenters via Enantioselective Alkene Hydroalkylation》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5c15430.html";
            },},{id: "news-祝贺课题组成员在-journal-of-the-american-chemical-society-上发表了论文-unifying-dearomatization-and-rearomatization-via-stereoselective-chlorination-dechlorination-resolution-of-axially-chiral-1-aryl-2-naphthols",
          title: '祝贺课题组成员在《Journal of the American Chemical Society》上发表了论文《Unifying Dearomatization and Rearomatization via Stereoselective Chlorination/Dechlorination: Resolution...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5c15900.html";
            },},{id: "news-祝贺课题组成员在-nature-communications-上发表了论文-unveiling-mechanistic-patterns-of-copper-catalyzed-radical-bond-formation-through-linear-free-energy-relationship",
          title: '祝贺课题组成员在《Nature Communications》上发表了论文《Unveiling mechanistic patterns of copper-catalyzed radical bond formation through linear free energy...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41467-025-67770-w.html";
            },},{id: "news-祝贺课题组成员在-nature-chemistry-上发表了论文-stepwise-controllable-catalytic-asymmetric-atherton-todd-reaction-to-access-diverse-p-v-stereogenic-compounds",
          title: '祝贺课题组成员在《Nature Chemistry》上发表了论文《Stepwise-controllable catalytic asymmetric Atherton–Todd reaction to access diverse P(V)-stereogenic compounds》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41557-025-02025-1.html";
            },},{id: "news-祝贺课题组成员在-nature-chemistry-上发表了论文-thermal-2-2-cycloaddition-as-a-route-to-gem-difluoro-heterobicyclo-n-1-1-alkanes",
          title: '祝贺课题组成员在《Nature Chemistry》上发表了论文《Thermal [2+2] cycloaddition as a route to gem-difluoro heterobicyclo[n.1.1]alkanes》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41557-025-02047-9.html";
            },},{id: "news-祝贺课题组成员在-jacs-au-上发表了论文-larger-substituents-enhance-stereospecificity-in-1-1-diazene-nitrogen-extrusion-through-attenuation-of-dynamic-mismatching",
          title: '祝贺课题组成员在《JACS Au》上发表了论文《Larger Substituents Enhance Stereospecificity in 1,1-Diazene Nitrogen Extrusion through Attenuation of Dynamic...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacsau.5c01603.html";
            },},{id: "news-祝贺课题组成员在-angewandte-chemie-international-edition-上发表了论文-data-driven-modeling-of-n-n-dioxide-metal-catalyzed-asymmetric-michael-additions",
          title: '祝贺课题组成员在《Angewandte Chemie International Edition》上发表了论文《Data‐Driven Modeling of N,N′‐Dioxide/Metal‐Catalyzed Asymmetric Michael Additions》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.202518560.html";
            },},{id: "news-祝贺课题组成员在-chemcatchem-上发表了论文-computational-insights-into-enantioselectivity-differences-in-pseudoenantiomeric-cinchona-alkaloid-catalyzed-imine-umpolung-michael-additions",
          title: '祝贺课题组成员在《ChemCatChem》上发表了论文《Computational Insights Into Enantioselectivity Differences in Pseudoenantiomeric Cinchona Alkaloid‐Catalyzed Imine Umpolung Michael Additions》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_cctc.70727.html";
            },},{id: "news-祝贺课题组成员在-chemistry-a-european-journal-上发表了论文-transforming-molecular-synthesis-with-large-language-models",
          title: '祝贺课题组成员在《Chemistry – A European Journal》上发表了论文《Transforming Molecular Synthesis With Large Language Models.》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_chem.71074.html";
            },},{id: "news-祝贺课题组成员在-chemistry-a-european-journal-上发表了论文-asymmetric-desymmetrization-of-para-quinamines-via-3-2-cycloaddition-with-1-3-5-triazinanes",
          title: '祝贺课题组成员在《Chemistry – A European Journal》上发表了论文《Asymmetric Desymmetrization of para‐Quinamines via (3+2) Cycloaddition With 1,3,5‐Triazinanes》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_chem.71220.html";
            },},{id: "projects-project-7",
          title: 'project 7',
          description: "with background image",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/7_project.html";
            },},{id: "projects-project-8",
          title: 'project 8',
          description: "an other project with a background image and giscus comments",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/8_project.html";
            },},{id: "projects-project-9",
          title: 'project 9',
          description: "another project with an image 🎉",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/9_project.html";
            },},{id: "projects-project-1",
          title: 'project 1',
          description: "with background image",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/en-us/1_project.html";
            },},{id: "projects-project-2",
          title: 'project 2',
          description: "a project with a background image and giscus comments",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/en-us/2_project.html";
            },},{id: "projects-project-3-with-very-long-name",
          title: 'project 3 with very long name',
          description: "a project that redirects to another website",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/en-us/3_project.html";
            },},{id: "projects-project-4",
          title: 'project 4',
          description: "another without an image",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/en-us/4_project.html";
            },},{id: "projects-project-5",
          title: 'project 5',
          description: "a project with a background image",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/en-us/5_project.html";
            },},{id: "projects-project-6",
          title: 'project 6',
          description: "a project with no image",
          section: "项目",handler: () => {
              window.location.href = "/zh-cn/projects/en-us/6_project.html";
            },},{
        id: 'social-email',
        title: '发送邮件',
        section: '社交账号',
        handler: () => {
          window.open("mailto:%79%6F%75@%65%78%61%6D%70%6C%65.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-inspire',
        title: 'Inspire HEP',
        section: '社交账号',
        handler: () => {
          window.open("https://inspirehep.net/authors/1010907", "_blank");
        },
      },{
        id: 'social-rss',
        title: 'RSS Feed',
        section: '社交账号',
        handler: () => {
          window.open("/feed.xml", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: '社交账号',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=qc6CJjYAAAAJ", "_blank");
        },
      },{
        id: 'social-custom_social',
        title: 'Custom_social',
        section: '社交账号',
        handler: () => {
          window.open("https://www.alberteinstein.com/", "_blank");
        },
      },{
          id: 'lang-en-us',
          title: 'en-us',
          section: '语言',
          handler: () => {
            window.location.href = "" + updatedUrl;
          },
        },{
      id: 'light-theme',
      title: '切换至浅色主题',
      description: '将网站主题切换为浅色',
      section: '主题',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: '切换至深色主题',
      description: '将网站主题切换为深色',
      section: '主题',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: '使用系统默认主题',
      description: '将网站主题切换为系统默认',
      section: '主题',
      handler: () => {
        setThemeSetting("system");
      },
    },];
