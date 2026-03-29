
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
            },},{id: "news-祝贺洪鑫在-chemical-science-上发表了论文-nickel-catalyzed-amination-of-aryl-carbamates-and-sequential-site-selective-cross-couplings",
          title: '祝贺洪鑫在《Chemical Science》上发表了论文《Nickel-catalyzed amination of aryl carbamates and sequential site-selective cross-couplings》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1039_c1sc00230a.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-origins-of-ligand-controlled-selectivities-in-ni-nhc-catalyzed-intramolecular-5-2-cycloadditions-and-homo-ene-reactions-a-theoretical-study",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Mechanism and Origins of Ligand-Controlled Selectivities in [Ni(NHC)]-Catalyzed...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja309873z.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-origins-of-selectivity-in-ru-ii-catalyzed-intramolecular-5-2-cycloadditions-and-ene-reactions-of-vinylcyclopropanes-and-alkynes-from-density-functional-theory",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Mechanism and Origins of Selectivity in Ru(II)-Catalyzed Intramolecular...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja4012657.html";
            },},{id: "news-祝贺洪鑫在-chem-sci-上发表了论文-distortion-accelerated-cycloadditions-and-strain-release-promoted-cycloreversions-in-the-organocatalytic-carbonyl-olefin-metathesis",
          title: '祝贺洪鑫在《Chem. Sci.》上发表了论文《Distortion-accelerated cycloadditions and strain-release-promoted cycloreversions in the organocatalytic carbonyl-olefin metathesis》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1039_c3sc52882k.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-mechanisms-and-origins-of-switchable-chemoselectivity-of-ni-catalyzed-c-aryl-o-and-c-acyl-o-activation-of-aryl-esters-with-phosphine-ligands",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Mechanisms and Origins of Switchable Chemoselectivity of Ni-Catalyzed...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja4118413.html";
            },},{id: "news-祝贺洪鑫在-organic-letters-上发表了论文-how-tethers-control-the-chemo-and-regioselectivities-of-intramolecular-cycloadditions-between-aryl-1-aza-2-azoniaallenes-and-alkenes",
          title: '祝贺洪鑫在《Organic Letters》上发表了论文《How Tethers Control the Chemo- and Regioselectivities of Intramolecular Cycloadditions between Aryl-1-aza-2-azoniaallenes...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ol501958s.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-selectivity-of-n-triflylphosphoramide-catalyzed-3-2-cycloaddition-between-hydrazones-and-alkenes",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Mechanism and Selectivity of N-Triflylphosphoramide Catalyzed (3(+)+2) Cycloaddition...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja506660c.html";
            },},{id: "news-祝贺洪鑫在-organic-letters-上发表了论文-why-alkynyl-substituents-dramatically-accelerate-hexadehydro-diels-alder-hdda-reactions-stepwise-mechanisms-of-hdda-cycloadditions",
          title: '祝贺洪鑫在《Organic Letters》上发表了论文《Why Alkynyl Substituents Dramatically Accelerate Hexadehydro-Diels-Alder (HDDA) Reactions: Stepwise Mechanisms of HDDA...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ol502780w.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-reactivity-and-chemoselectivity-of-allenes-in-rh-i-catalyzed-intermolecular-5-2-cycloadditions-with-vinylcyclopropanes-allene-mediated-rhodacycle-formation-can-poison-rh-i-catalyzed-cycloadditions",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Reactivity and Chemoselectivity of Allenes in Rh(I)-Catalyzed Intermolecular...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja5098308.html";
            },},{id: "news-祝贺洪鑫在-the-journal-of-organic-chemistry-上发表了论文-mechanism-reactivity-and-selectivity-of-nickel-catalyzed-4-4-2-cycloadditions-of-dienes-and-alkynes",
          title: '祝贺洪鑫在《The Journal of Organic Chemistry》上发表了论文《Mechanism, Reactivity, and Selectivity of Nickel-Catalyzed [4+4+2] Cycloadditions of...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jo502219d.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-ni-nhc-catalyzed-cycloaddition-of-diynes-and-tropone-apparent-enone-cycloaddition-involving-an-8-pi-insertion",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Ni(NHC)]-Catalyzed Cycloaddition of Diynes and Tropone: Apparent Enone...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_ja5105206.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-iodoarene-catalyzed-stereospecific-intramolecular-sp-3-c-h-amination-reaction-development-and-mechanistic-insights",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Iodoarene-Catalyzed Stereospecific Intramolecular sp(3) C-H Amination: Reaction Development...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5b03488.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-mechanism-and-dynamics-of-intramolecular-c-h-insertion-reactions-of-1-aza-2-azoniaallene-salts",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Mechanism and Dynamics of Intramolecular C-H Insertion Reactions...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.5b04474.html";
            },},{id: "news-祝贺洪鑫在-nature-上发表了论文-conversion-of-amides-to-esters-by-the-nickel-catalysed-activation-of-amide-c-n-bonds",
          title: '祝贺洪鑫在《Nature》上发表了论文《Conversion of amides to esters by the nickel-catalysed activation of amide C-N bonds》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_nature14615.html";
            },},{id: "news-祝贺洪鑫在-acs-catalysis-上发表了论文-computational-exploration-of-mechanism-and-selectivities-of-nhc-nickel-ii-hydride-catalyzed-hydroalkenylations-of-styrene-with-alpha-olefins",
          title: '祝贺洪鑫在《ACS Catalysis》上发表了论文《Computational Exploration of Mechanism and Selectivities of (NHC)Nickel(II)hydride-Catalyzed Hydroalkenylations of Styrene with...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.5b01075.html";
            },},{id: "news-祝贺洪鑫在-acs-central-science-上发表了论文-mechanistic-insights-into-two-phase-radical-c-h-arylations",
          title: '祝贺洪鑫在《ACS Central Science》上发表了论文《Mechanistic Insights into Two-Phase Radical C-H Arylations》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscentsci.5b00332.html";
            },},{id: "news-祝贺洪鑫在-organic-letters-上发表了论文-ligand-controlled-diastereoselective-1-3-dipolar-cycloadditions-of-azomethine-ylides-with-methacrylonitrile",
          title: '祝贺洪鑫在《Organic Letters》上发表了论文《Ligand-Controlled Diastereoselective 1,3-Dipolar Cycloadditions of Azomethine Ylides with Methacrylonitrile》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.orglett.5b03171.html";
            },},{id: "news-祝贺洪鑫在-angewandte-chemie-international-edition-上发表了论文-nickel-catalyzed-activation-of-acyl-c-o-bonds-of-methyl-esters",
          title: '祝贺洪鑫在《Angewandte Chemie International Edition》上发表了论文《Nickel-Catalyzed Activation of Acyl C-O Bonds of Methyl Esters》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.201511486.html";
            },},{id: "news-祝贺洪鑫在-acs-catalysis-上发表了论文-how-doped-mos2-breaks-transition-metal-scaling-relations-for-co2-electrochemical-reduction",
          title: '祝贺洪鑫在《ACS Catalysis》上发表了论文《How Doped MoS2 Breaks Transition-Metal Scaling Relations for CO2 Electrochemical Reduction》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acscatal.6b00619.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-distortion-controlled-reactivity-and-molecular-dynamics-of-dehydro-diels-alder-reactions",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Distortion-Controlled Reactivity and Molecular Dynamics of Dehydro-Diels-Alder Reactions》！...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.6b04113.html";
            },},{id: "news-祝贺洪鑫在-science-上发表了论文-ligand-accelerated-enantioselective-methylene-c-sp-3-h-bond-activation",
          title: '祝贺洪鑫在《Science》上发表了论文《Ligand-accelerated enantioselective methylene C(sp(3))-H bond activation》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1126_science.aaf4434.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-palladium-catalyzed-suzuki-miyaura-coupling-of-aryl-esters",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Palladium-Catalyzed Suzuki-Miyaura Coupling of Aryl Esters》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.6b12329.html";
            },},{id: "news-祝贺洪鑫在-the-journal-of-organic-chemistry-上发表了论文-2-1-cycloaddition-reactions-give-further-evidence-of-the-nitrenium-like-character-of-1-aza-2-azoniaallene-salts",
          title: '祝贺洪鑫在《The Journal of Organic Chemistry》上发表了论文《(2+1)-Cycloaddition Reactions Give Further Evidence of the Nitrenium-like Character...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_acs.joc.7b00407.html";
            },},{id: "news-祝贺洪鑫在-nature-communications-上发表了论文-understanding-trends-in-electrochemical-carbon-dioxide-reduction-rates",
          title: '祝贺洪鑫在《Nature Communications》上发表了论文《Understanding trends in electrochemical carbon dioxide reduction rates》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_ncomms15438.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-mechanisms-and-origins-of-chemo-and-regioselectivities-of-ru-ii-catalyzed-decarboxylative-c-h-alkenylation-of-aryl-carboxylic-acids-with-alkynes-a-computational-study",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《Mechanisms and Origins of Chemo- and Regioselectivities of...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.7b00714.html";
            },},{id: "news-祝贺洪鑫在-journal-of-the-american-chemical-society-上发表了论文-the-origins-of-dramatic-differences-in-five-membered-vs-six-membered-chelation-of-pd-ii-on-efficiency-of-c-sp-3-h-bond-activation",
          title: '祝贺洪鑫在《Journal of the American Chemical Society》上发表了论文《The Origins of Dramatic Differences in Five-Membered vs...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1021_jacs.7b01801.html";
            },},{id: "news-祝贺洪鑫在-science-china-chemistry-上发表了论文-ni-mediated-c-n-activation-of-amides-and-derived-catalytic-transformations",
          title: '祝贺洪鑫在《Science China Chemistry》上发表了论文《Ni-mediated C–N activation of amides and derived catalytic transformations》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1007_s11426-017-9025-1.html";
            },},{id: "news-祝贺洪鑫在-molecules-上发表了论文-computational-study-of-mechanism-and-thermodynamics-of-ni-ipr-catalyzed-amidation-of-esters",
          title: '祝贺洪鑫在《Molecules》上发表了论文《Computational Study of Mechanism and Thermodynamics of Ni/IPr-Catalyzed Amidation of Esters》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.3390_molecules23102681.html";
            },},{id: "news-祝贺汤缪炅在-angewandte-chemie-international-edition-上发表了论文-towards-data-driven-design-of-asymmetric-hydrogenation-of-olefins-database-and-hierarchical-learning",
          title: '祝贺汤缪炅在《Angewandte Chemie International Edition》上发表了论文《Towards Data‐Driven Design of Asymmetric Hydrogenation of Olefins: Database and...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.202106880.html";
            },},{id: "news-祝贺汤缪炅在-synlett-上发表了论文-a-molecular-stereostructure-descriptor-based-on-spherical-projection",
          title: '祝贺汤缪炅在《Synlett》上发表了论文《A Molecular Stereostructure Descriptor Based On Spherical Projection》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1055_s-0040-1705977.html";
            },},{id: "news-祝贺汤缪炅在-chemistry-an-asian-journal-上发表了论文-exploring-spectrum-based-molecular-descriptors-for-reaction-performance-prediction",
          title: '祝贺汤缪炅在《Chemistry – An Asian Journal》上发表了论文《Exploring Spectrum‐based Molecular Descriptors for Reaction Performance Prediction》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_asia.202300011.html";
            },},{id: "news-祝贺汤缪炅在-chinese-science-bulletin-上发表了论文-数据驱动的有机分子理化性质预测",
          title: '祝贺汤缪炅在《Chinese Science Bulletin》上发表了论文《数据驱动的有机分子理化性质预测》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1360_tb-2024-0812.html";
            },},{id: "news-祝贺汤缪炅在-scientific-data-上发表了论文-qm9star-two-million-dft-computed-equilibrium-structures-for-ions-and-radicals-with-atomic-information",
          title: '祝贺汤缪炅在《Scientific Data》上发表了论文《QM9star, two Million DFT-computed Equilibrium Structures for Ions and Radicals with Atomic...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41597-024-03933-6.html";
            },},{id: "news-祝贺洪鑫在-science-advances-上发表了论文-rhodium-catalyzed-atropodivergent-hydroamination-of-alkynes-by-leveraging-two-potential-enantiodetermining-steps",
          title: '祝贺洪鑫在《Science Advances》上发表了论文《Rhodium-Catalyzed Atropodivergent Hydroamination of Alkynes by Leveraging Two Potential Enantiodetermining Steps》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1126_sciadv.adr4435.html";
            },},{id: "news-祝贺汤缪炅在-organic-amp-amp-biomolecular-chemistry-上发表了论文-using-machine-learning-methods-to-predict-the-diabatic-bond-dissociation-energy-of-non-heme-iron-complexes",
          title: '祝贺汤缪炅在《Organic &amp;amp;amp; Biomolecular Chemistry》上发表了论文《Using machine learning methods to predict the diabatic bond dissociation...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1039_d5ob00007f.html";
            },},{id: "news-祝贺洪鑫在-science-上发表了论文-asymmetric-amination-of-alkyl-radicals-with-two-minimally-different-alkyl-substituents",
          title: '祝贺洪鑫在《Science》上发表了论文《Asymmetric amination of alkyl radicals with two minimally different alkyl substituents》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1126_science.adu3996.html";
            },},{id: "news-祝贺汤缪炅在-nature-machine-intelligence-上发表了论文-a-unified-pre-trained-deep-learning-framework-for-cross-task-reaction-performance-prediction-and-synthesis-planning",
          title: '祝贺汤缪炅在《Nature Machine Intelligence》上发表了论文《A unified pre-trained deep learning framework for cross-task reaction performance prediction...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s42256-025-01098-4.html";
            },},{id: "news-祝贺洪鑫在-inorganics-上发表了论文-theoretical-study-on-the-ortho-para-reactivity-difference-in-ru-catalyzed-amination-of-aminopyridines-via-η6-coordination-role-of-meisenheimer-intermediate-coordination-ability",
          title: '祝贺洪鑫在《Inorganics》上发表了论文《Theoretical Study on the Ortho–Para Reactivity Difference in Ru-Catalyzed Amination of Aminopyridines via...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.3390_inorganics13100316.html";
            },},{id: "news-祝贺汤缪炅在-nature-communications-上发表了论文-unveiling-mechanistic-patterns-of-copper-catalyzed-radical-bond-formation-through-linear-free-energy-relationship",
          title: '祝贺汤缪炅在《Nature Communications》上发表了论文《Unveiling mechanistic patterns of copper-catalyzed radical bond formation through linear free energy...',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1038_s41467-025-67770-w.html";
            },},{id: "news-祝贺汤缪炅在-angewandte-chemie-international-edition-上发表了论文-data-driven-modeling-of-n-n-dioxide-metal-catalyzed-asymmetric-michael-additions",
          title: '祝贺汤缪炅在《Angewandte Chemie International Edition》上发表了论文《Data‐Driven Modeling of N,N′‐Dioxide/Metal‐Catalyzed Asymmetric Michael Additions》！',
          description: "",
          section: "动态",handler: () => {
              window.location.href = "/zh-cn/news/zh-cn/10.1002_anie.202518560.html";
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
