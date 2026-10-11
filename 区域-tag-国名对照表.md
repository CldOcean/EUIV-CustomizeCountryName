# EU4 区域 - TAG - 国名对照表

> 由 `tools/build_region_tag_table.py` 从以下数据源自动生成，可随时重跑：
>
> - 游戏本体 `common/country_tags/00_countries.txt`（TAG 清单）
> - 游戏本体 `history/countries/TAG - Xxx.txt`（首都省份）
> - 游戏本体 `map/area.txt` → `map/region.txt` → `map/superregion.txt`（省份→地区→区域→大区）
> - 游戏本体 `localisation/*_l_english.yml`（英文原名）
> - 汉化模组 `Chinese Language Mod for 1.37`（workshop 2976470733）`localisation/*_l_english.yml`（中文国名，转义态已解码）

## 分类规则

归类依据 = **该 TAG 首都省份所在的游戏 region**。与 wiki 的分类一致（wiki 同样是首都定区域），
三处 wiki 与游戏文件叫法不同的地方按以下口径处理：

| 大区 | 包含的游戏 region | 说明 |
|---|---|---|
| 中华区域 | 北中国、西南、南中国 | 从东亚中单独挑出 |
| 东亚区域 | 朝鲜、日本 | 满洲已划走 |
| 鞑靼大区 | 蒙古、西藏、中亚、西西伯利亚、东西伯利亚、满洲 | 满洲按你的要求并入鞑靼（游戏里满洲属 far_east） |
| 西欧区域 | 法兰西、伊比利亚、不列颠群岛、低地国家 | 斯堪的纳维亚、意大利已划走 |
| 中欧区域 | 北德意志、南德意志、斯堪的纳维亚、意大利 | = 北德意志 + 南德意志 + 斯堪的纳维亚 + 意大利（游戏无「中欧」概念，按你的口径） |
| 东欧区域 | 波兰、波罗的、俄罗斯、鲁塞尼亚、喀尔巴阡、巴尔干、克里米亚、乌拉尔 | 含巴尔干，故奥斯曼（首都埃迪尔内）落在东欧 |
| 中东区域 | 安纳托利亚、马什里克、阿拉伯、埃及、波斯、呼罗珊、高加索 | 近东大区 + 波斯大区（波斯/呼罗珊/高加索一并并入） |
| 北非区域 | 马格里布、萨赫勒、尼日尔、几内亚、非洲之角 | = 游戏的 africa 大区（马格里布+萨赫勒+尼日尔+几内亚+非洲之角） |
| 南非区域 | 东非、刚果、南非、中非 | = 游戏的 southern_africa 大区（撒哈拉以南） |
| 印度大区 | 印度斯坦、孟加拉、西印度、德干、科罗曼德尔 | 同上 |
| 东印度大区 | 缅甸、马来、摩鹿加、印度尼西亚、中南半岛 | 含中南半岛、南洋诸岛 |
| 大洋洲大区 | 大洋洲、澳大利亚 | 同上 |
| 北美大区 | 哈德逊湾、卡斯卡迪亚、大平原、密西西比、北美东南、北美东北、五大湖、加拿大 | 同上 |
| 中南美区域 | 中美洲、墨西哥、加勒比、里奥格兰德、加利福尼亚、巴西、哥伦比亚、秘鲁、上秘鲁、拉普拉塔 | 中美洲+墨西哥+加勒比+里奥格兰德+加州 与 南美三区合并 |

## 汇总

| 大区 | TAG 数 |
|---|---|
| 中华区域 | 25 |
| 东亚区域 | 41 |
| 鞑靼大区 | 41 |
| 西欧区域 | 71 |
| 中欧区域 | 125 |
| 东欧区域 | 71 |
| 中东区域 | 78 |
| 北非区域 | 77 |
| 南非区域 | 43 |
| 印度大区 | 104 |
| 东印度大区 | 78 |
| 大洋洲大区 | 35 |
| 北美大区 | 96 |
| 中南美区域 | 86 |
| **合计** | **971** |
| 特殊标签（REB / PIR / NAT） | 3 |

---

## 中华区域（25）

### 北中国（9）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CSH` | 顺 | Shun |
| `JIN` | 晋 | Jin |
| `LNG` | 梁 | Liang |
| `QIC` | 齐 | Qi |
| `QIN` | 秦 | Qin |
| `QNG` | 清 | Qing |
| `TNG` | 唐 | Tang |
| `YAN` | 燕 | Yan |
| `YUA` | 元 | Yuan |

### 西南（5）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CDL` | 大理 | Dali |
| `CYI` | 彝 | Yi |
| `CZH` | 周 | Zhou |
| `MMA` | 孟卯 | Mong Mao |
| `SHU` | 蜀 | Shu |

### 南中国（11）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CGS` | 长生 | Changsheng |
| `CHC` | 楚 | Chu |
| `CMI` | 苗 | Miao |
| `CXI` | 西 | Xi |
| `FRM` | 东宁 | Tungning |
| `HUA` | 淮 | Huai |
| `MIN` | 闽 | Min |
| `MNG` | 明 | Ming |
| `NNG` | 宁 | Ning |
| `WUU` | 吴 | Wu |
| `YUE` | 越 | Yue |

---

## 东亚区域（41）

### 朝鲜（1）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `KOR` | 朝鲜 | Korea |

### 日本（40）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AKM` | 赤松 | Akamatsu |
| `AKT` | 安东 | Ando |
| `AMA` | 尼子 | Amago |
| `ANU` | 阿伊努 | Ainu |
| `ASA` | 朝仓 | Asakura |
| `ASK` | 足利 | Ashikaga |
| `CBA` | 千叶 | Chiba |
| `CSK` | 长宗我部 | Chosokabe |
| `DTE` | 伊达 | Date |
| `HJO` | 北条 | Hojo |
| `HSK` | 细川 | Hosokawa |
| `HTK` | 畠山 | Hatakeyama |
| `IKE` | 池田 | Ikeda |
| `IMG` | 今川 | Imagawa |
| `ISK` | 一色 | Isshiki |
| `ITO` | 伊东 | Ito |
| `JAP` | 日本 | Japan |
| `KKC` | 菊池 | Kikuchi |
| `KNO` | 河野 | Kono |
| `KTB` | 北畠 | Kitabatake |
| `MAE` | 前田 | Maeda |
| `MRI` | 毛利 | Mori |
| `ODA` | 织田 | Oda |
| `OGS` | 小笠原 | Ogasawara |
| `OTM` | 大友 | Otomo |
| `OUC` | 大内 | Ouchi |
| `RFR` | 南部 | Nanbu |
| `RYU` | 琉球 | Ryukyu |
| `SBA` | 斯波 | Shiba |
| `SHN` | 少贰 | Shoni |
| `SMZ` | 岛津 | Shimazu |
| `SOO` | 宗 | So |
| `STK` | 佐竹 | Satake |
| `TKD` | 武田 | Takeda |
| `TKG` | 德川 | Tokugawa |
| `TKI` | 土岐 | Toki |
| `TTI` | 筒井 | Tsutsui |
| `UES` | 上杉 | Uesugi |
| `UTN` | 宇都宫 | Utsunomiya |
| `YMN` | 山名 | Yamana |

---

## 鞑靼大区（41）

### 蒙古（9）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CHG` | 东察合台 | Moghulistan |
| `CHH` | 察哈尔 | Chahar |
| `HMI` | 哈密 | Kara Del |
| `KHA` | 蒙古 | Mongolia |
| `KLK` | 喀尔喀 | Khalkha |
| `KRC` | 科尔沁 | Korchin |
| `MGE` | 蒙古帝国 | Mongol Empire |
| `OIR` | 瓦剌 | Oirat |
| `ZUN` | 准噶尔 | Dzungar |

### 西藏（9）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BHU` | 不丹 | Bhutan |
| `GUG` | 古格 | Guge |
| `KAM` | 康 | Kham |
| `KSD` | 和硕特 | Khoshuud |
| `PHA` | 卫 | U |
| `SKK` | 锡金 | Sikkim |
| `SYG` | 撒里畏吾尔 | Sarig Yogir |
| `TIB` | 吐蕃 | Tibet |
| `UTS` | 藏 | Tsang |

### 中亚（8）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BUK` | 布哈拉 | Bukhara |
| `KAS` | 叶尔羌 | Yarkand |
| `KHI` | 希瓦 | Khiva |
| `KOK` | 费尔干纳 | Ferghana |
| `KZH` | 哈萨克 | Kazakh |
| `NOG` | 诺盖 | Nogai |
| `TIM` | 帖木儿 | Timurids |
| `TRS` | 河中 | Transoxiana |

### 西西伯利亚（2）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `SHY` | 乌兹别克 | Uzbek |
| `SIB` | 西伯利亚 | Sibir |

### 东西伯利亚（5）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BRT` | 布里亚特 | Buryatia |
| `CHU` | 楚科奇 | Chukchi |
| `CHV` | 察夫楚万尼 | Chavchuveny |
| `HOD` | 霍京 | Khodynt |
| `KMC` | 堪察加 | Kamchadals |

### 满洲（8）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `EJZ` | 赫哲 | Nanai |
| `MCH` | 满洲 | Manchu |
| `MHX` | 海西女真 | Haixi |
| `MJZ` | 建州女真 | Jianzhou |
| `MYR` | 锡伯 | Xibe |
| `NHX` | 鄂罗奇 | Orochoni |
| `NVK` | 尼夫赫 | Nivkh |
| `SOL` | 索伦 | Solon |

---

## 西欧区域（71）

### 法兰西（23）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ALE` | 阿朗松 | Alençon |
| `AMG` | 阿马尼亚克 | Armagnac |
| `AUV` | 奥弗涅 | Auvergne |
| `AVE` | 安茹王国 | Angevin Kingdom |
| `AVI` | 阿维尼翁 | Avignon |
| `BAR` | 巴尔 | Bar |
| `BER` | 贝里 | Berry |
| `BOU` | 波旁 | Bourbonnais |
| `BRI` | 布列塔尼 | Brittany |
| `BUR` | 勃艮第 | Burgundy |
| `CHP` | 香槟 | Champagne |
| `DAU` | 多菲内 | Dauphine |
| `FOI` | 富瓦 | Foix |
| `FRA` | 法兰西 | France |
| `GUY` | 加斯科涅 | Gascony |
| `LOR` | 洛林 | Lorraine |
| `NEV` | 讷韦尔 | Nevers |
| `NRM` | 诺曼底 | Normandy |
| `ORL` | 奥尔良 | Orleans |
| `PIC` | 皮卡第 | Picardy |
| `PRO` | 普罗旺斯 | Provence |
| `SAV` | 萨伏依 | Savoy |
| `TOU` | 图卢兹 | Toulouse |

### 伊比利亚（13）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ADU` | 安达卢西亚 | Andalusia |
| `ARA` | 阿拉贡 | Aragon |
| `ASU` | 阿斯图里亚斯 | Asturias |
| `CAS` | 卡斯蒂利亚 | Castile |
| `CAT` | 加泰罗尼亚 | Catalonia |
| `GAL` | 加利西亚 | Galicia |
| `GRA` | 格拉纳达 | Granada |
| `LON` | 莱昂 | León |
| `MJO` | 马略卡 | Majorca |
| `NAV` | 纳瓦拉 | Navarra |
| `POR` | 葡萄牙 | Portugal |
| `SPA` | 西班牙 | Spain |
| `VAL` | 巴伦西亚 | Valencia |

### 不列颠群岛（24）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CNN` | 克兰里卡德 | Clanricarde |
| `CRN` | 康沃尔 | Cornwall |
| `DMS` | 德斯蒙德 | Desmond |
| `ENG` | 英格兰 | England |
| `FLY` | 奥法利 | Offaly |
| `GBR` | 大不列颠 | Great Britain |
| `HSC` | 盖尔 | Gaeldom |
| `IRE` | 爱尔兰 | Ireland |
| `KID` | 基尔代尔 | Kildare |
| `KOI` | 马恩 | Mann |
| `LEI` | 伦斯特 | Leinster |
| `LOI` | 群岛 | The Isles |
| `MCM` | 芒斯特 | Munster |
| `MNS` | 托蒙德 | Thomond |
| `MTH` | 米斯 | Meath |
| `NOL` | 诺森伯兰 | Northumberland |
| `ORD` | 奥蒙德 | Ormond |
| `SCO` | 苏格兰 | Scotland |
| `SLE` | 塞拉 | Salé |
| `SLN` | 斯莱戈 | Sligo |
| `TRY` | 蒂康奈尔 | Tyrconnell |
| `TYR` | 蒂龙 | Tyrone |
| `ULS` | 阿尔斯特 | Ulster |
| `WLS` | 威尔士 | Wales |

### 低地国家（11）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BRB` | 布拉班特 | Brabant |
| `EFR` | 东弗里斯兰 | East Frisia |
| `FLA` | 佛兰德 | Flanders |
| `FRI` | 弗里斯兰 | Friesland |
| `GEL` | 海尔雷 | Gelre |
| `HAI` | 埃诺 | Hainaut |
| `HOL` | 荷兰 | Holland |
| `LIE` | 列日 | Liege |
| `LUX` | 卢森堡 | Luxembourg |
| `NED` | 尼德兰 | Netherlands |
| `UTR` | 乌得勒支 | Utrecht |

---

## 中欧区域（125）

### 北德意志（47）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AAC` | 亚琛 | Aachen |
| `ANH` | 安哈尔特 | Anhalt |
| `BOH` | 波希米亚 | Bohemia |
| `BRA` | 勃兰登堡 | Brandenburg |
| `BRE` | 不来梅 | Bremen |
| `BRG` | 贝格 | Berg |
| `BRU` | 不伦瑞克 | Brunswick |
| `CLB` | 卡伦贝格 | Calenberg |
| `DTT` | 迪特马尔申 | Dithmarschen |
| `FRN` | 法兰克福 | Frankfurt |
| `GER` | 德意志 | Germany |
| `GMA` | 大摩拉维亚 | Great Moravia |
| `GOS` | 戈斯拉尔 | Goslar |
| `HAM` | 汉堡 | Hamburg |
| `HAN` | 汉诺威 | Hanover |
| `HES` | 黑森 | Hesse |
| `HSA` | 吕贝克 | Lübeck |
| `KLE` | 克莱沃 | Cleves |
| `KOL` | 科隆 | Cologne |
| `LAU` | 萨克森-劳恩堡 | Saxe-Lauenburg |
| `LOT` | 洛塔林吉亚 | Lotharingia |
| `LPP` | 利珀 | Lippe |
| `LUN` | 吕讷堡 | Lüneburg |
| `MAG` | 马格德堡 | Magdeburg |
| `MAI` | 美因茨 | Mainz |
| `MEI` | 迈森 | Meissen |
| `MKL` | 梅克伦堡 | Mecklenburg |
| `MUN` | 明斯特 | Münster |
| `MVA` | 摩拉维亚 | Moravia |
| `NSA` | 拿骚 | Nassau |
| `OLD` | 奥尔登堡 | Oldenburg |
| `OSN` | 奥斯纳布吕克 | Osnabrück |
| `PAD` | 帕德博恩 | Paderborn |
| `POM` | 波美拉尼亚 | Pomerania |
| `RUG` | 吕根 | Rügen |
| `RUP` | 鲁平 | Ruppin |
| `RVA` | 多特蒙德 | Dortmund |
| `SAX` | 萨克森 | Saxony |
| `SHL` | 荷尔斯泰因 | Holstein |
| `SOR` | 卢萨蒂亚 | Lusatia |
| `STE` | 斯德丁 | Stettin |
| `SYN` | 智械 | Synthetics |
| `THU` | 图林根 | Thuringia |
| `TRI` | 特里尔 | Trier |
| `VER` | 费尔登 | Verden |
| `WES` | 威斯特伐利亚 | Westphalia |
| `WOL` | 沃尔加斯特 | Wolgast |

### 南德意志（37）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ALS` | 斯特拉斯堡 | Strasbourg |
| `ANS` | 安斯巴赫 | Ansbach |
| `AUG` | 奥格斯堡 | Augsburg |
| `AUH` | 奥地利-匈牙利 | Austria-Hungary |
| `BAD` | 巴登 | Baden |
| `BAM` | 班贝格 | Bamberg |
| `BAV` | 巴伐利亚 | Bavaria |
| `BYT` | 拜罗伊特 | Bayreuth |
| `CLI` | 采列 | Cilli |
| `COB` | 科堡 | Coburg |
| `DWT` | 多瑙沃特 | Donauwörth |
| `FKN` | 法兰克尼亚 | Franconia |
| `GNV` | 日内瓦 | Geneva |
| `HAB` | 奥地利 | Austria |
| `HLR` | 神圣罗马帝国 | Holy Roman Empire |
| `ING` | 英戈尔施塔特 | Ingolstadt |
| `KNZ` | 康斯坦茨 | Konstanz |
| `LBV` | 兰茨胡特 | Landshut |
| `MBZ` | 布雷根茨 | Bregenz |
| `MEM` | 梅明根 | Memmingen |
| `MLH` | 米卢斯 | Mulhouse |
| `NUM` | 纽伦堡 | Nuremberg |
| `PAL` | 普法尔茨 | The Palatinate |
| `PSS` | 帕绍 | Passau |
| `REG` | 雷根斯堡 | Regensburg |
| `ROT` | 罗滕堡 | Rothenburg |
| `SLZ` | 萨尔茨堡 | Salzburg |
| `STY` | 施蒂里亚 | Styria |
| `SWA` | 施瓦本 | Swabia |
| `SWI` | 瑞士 | Switzerland |
| `TIR` | 蒂罗尔 | Tirol |
| `TNT` | 特伦托 | Trent |
| `TTL` | 三同盟 | Three Leagues |
| `UBV` | 慕尼黑 | Munich |
| `ULM` | 乌尔姆 | Ulm |
| `WBG` | 维尔茨堡 | Wurzburg |
| `WUR` | 符腾堡 | Wurttemberg |

### 斯堪的纳维亚（9）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `DAN` | 丹麦 | Denmark |
| `FIN` | 芬兰 | Finland |
| `GOT` | 哥得兰 | Gotland |
| `ICE` | 冰岛 | Iceland |
| `JMN` | 扬马延 | Jan Mayen |
| `NOR` | 挪威 | Norway |
| `SCA` | 斯堪的纳维亚 | Scandinavia |
| `SMI` | 萨米 | Sápmi |
| `SWE` | 瑞典 | Sweden |

### 意大利（32）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AQU` | 阿奎莱亚 | Aquileia |
| `BLG` | 博洛尼亚 | Bologna |
| `COR` | 科西嘉 | Corsica |
| `ETR` | 伊特鲁里亚 | Etruria |
| `FER` | 费拉拉 | Ferrara |
| `GEN` | 热那亚 | Genoa |
| `ITA` | 意大利 | Italy |
| `JAI` | 马耳他 | Malta |
| `LAN` | 佛罗伦萨 | Florence |
| `LUC` | 卢卡 | Lucca |
| `MAN` | 曼托瓦 | Mantua |
| `MFA` | 蒙费拉托 | Montferrat |
| `MLO` | 米兰 | Milan |
| `MOD` | 摩德纳 | Modena |
| `NAP` | 那不勒斯 | Naples |
| `PAP` | 教宗国 | The Papal State |
| `PAR` | 帕尔马 | Parma |
| `PDV` | 帕多瓦 | Padua |
| `PGA` | 佩鲁贾 | Perugia |
| `PIS` | 比萨 | Pisa |
| `ROM` | 罗马帝国 | Roman Empire |
| `SAR` | 撒丁 | Sardinia |
| `SIC` | 西西里 | Sicily |
| `SIE` | 锡耶纳 | Siena |
| `SPI` | 撒丁-皮埃蒙特 | Sardinia-Piedmont |
| `SPL` | 斯波莱托 | Spoleto |
| `SZO` | 萨卢佐 | Saluzzo |
| `TTS` | 两西西里 | Two Sicilies |
| `TUS` | 托斯卡纳 | Tuscany |
| `URB` | 乌尔比诺 | Urbino |
| `VEN` | 威尼斯 | Venice |
| `VRN` | 维罗纳 | Verona |

---

## 东欧区域（71）

### 波兰（7）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `GLG` | 格沃古夫 | Glogow |
| `KRA` | 克拉科夫 | Krakow |
| `MAZ` | 马佐夫舍 | Mazovia |
| `OPL` | 奥波莱 | Opole |
| `PLC` | 波兰立陶宛联邦 | Commonwealth |
| `POL` | 波兰 | Poland |
| `SIL` | 西里西亚 | Silesia |

### 波罗的（10）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `DNZ` | 但泽 | Danzig |
| `EST` | 爱沙尼亚 | Estonia |
| `KUR` | 库尔兰 | Kurland |
| `LIT` | 立陶宛 | Lithuania |
| `LIV` | 利沃尼亚骑士团 | Livonian Order |
| `LTG` | 拉特加尔 | Latgalia |
| `LVA` | 利沃尼亚 | Livonia |
| `PRU` | 普鲁士 | Prussia |
| `RIG` | 里加 | Riga |
| `TEU` | 条顿骑士团 | Teutonic Order |

### 俄罗斯（13）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BLO` | 别洛奥泽罗 | Beloozero |
| `KRL` | 卡累利阿 | Karelia |
| `MOS` | 莫斯科 | Muscovy |
| `NOV` | 诺夫哥罗德 | Novgorod |
| `OKA` | 奥多耶夫 | Odoyev |
| `PLT` | 波洛茨克 | Polotsk |
| `PSK` | 普斯科夫 | Pskov |
| `QAS` | 卡西姆 | Qasim |
| `RSO` | 罗斯托夫 | Rostov |
| `RUS` | 俄罗斯 | Russia |
| `RYA` | 梁赞 | Ryazan |
| `TVE` | 特维尔 | Tver |
| `YAR` | 雅罗斯拉夫尔 | Yaroslavl |

### 鲁塞尼亚（5）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CHR` | 切尔尼戈夫 | Chernigov |
| `KIE` | 基辅 | Kiev |
| `SMO` | 斯摩棱斯克 | Smolensk |
| `UKR` | 鲁塞尼亚 | Ruthenia |
| `VOL` | 加利西亚-沃里尼亚 | Galicia–Volhynia |

### 喀尔巴阡（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `HUN` | 匈牙利 | Hungary |
| `MOL` | 摩尔达维亚 | Moldavia |
| `RMN` | 罗马尼亚 | Romania |
| `SLO` | 尼特拉 | Nitra |
| `TRA` | 特兰西瓦尼亚 | Transylvania |
| `WAL` | 瓦拉几亚 | Wallachia |

### 巴尔干（19）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ACH` | 亚该亚 | Achaea |
| `ALB` | 阿尔巴尼亚 | Albania |
| `ATH` | 雅典 | Athens |
| `BOS` | 波斯尼亚 | Bosnia |
| `BUL` | 保加利亚 | Bulgaria |
| `BYZ` | 拜占庭 | Byzantium |
| `CEP` | 科孚 | Corfu |
| `CRO` | 克罗地亚 | Croatia |
| `CRT` | 克里特 | Crete |
| `DAL` | 达尔马提亚 | Dalmatia |
| `EPI` | 伊庇鲁斯 | Epirus |
| `GRE` | 希腊 | Greece |
| `HRZ` | 黑塞哥维那 | Herzegovina |
| `LAE` | 拉丁帝国 | Latin Empire |
| `MOE` | 摩里亚 | Morea |
| `MON` | 黑山 | Montenegro |
| `RAG` | 拉古萨 | Ragusa |
| `SER` | 塞尔维亚 | Serbia |
| `TUR` | 奥斯曼 | Ottomans |

### 克里米亚（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AST` | 阿斯特拉罕 | Astrakhan |
| `CRI` | 克里米亚 | Crimea |
| `FEO` | 狄奥多罗 | Theodoro |
| `GOL` | 大帐 | Great Horde |
| `KLM` | 卡尔梅克 | Kalmyk |
| `ZAZ` | 扎波罗热 | Zaporozhie |

### 乌拉尔（5）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BSH` | 巴什基尔 | Bashkiria |
| `GLH` | 金帐 | Golden Horde |
| `KAZ` | 喀山 | Kazan |
| `NZH` | 下诺夫哥罗德 | Nizhny Novgorod |
| `PRM` | 彼尔姆 | Perm |

---

## 中东区域（78）

### 安纳托利亚（17）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AKK` | 白羊 | Aq Qoyunlu |
| `AYD` | 艾登 | Aydin |
| `BTL` | 比特利斯 | Bitlis |
| `CND` | 詹达尔 | Candar |
| `CYP` | 塞浦路斯 | Cyprus |
| `DUL` | 杜勒卡迪尔 | Dulkadir |
| `ERE` | 埃雷特纳 | Eretna |
| `GRM` | 格尔米扬 | Germiyan |
| `HSN` | 哈桑凯伊夫 | Hisn Kayfa |
| `KAR` | 卡拉曼 | Karaman |
| `KNI` | 医院骑士团 | The Knights |
| `MEN` | 门泰谢 | Mentese |
| `NAX` | 纳克索斯 | Naxos |
| `RAM` | 拉马赞 | Ramazan |
| `RUM` | 罗姆 | Rûm |
| `SRU` | 萨鲁汗 | Saruhan |
| `TRE` | 特拉比松 | Trebizond |

### 马什里克（7）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BSR` | 巴士拉 | Basra |
| `FAD` | 法德勒 | Fadl |
| `IRQ` | 伊拉克 | Iraq |
| `ISR` | 以色列 | Israel |
| `KOJ` | 耶路撒冷 | Jerusalem |
| `LEB` | 黎巴嫩 | Lebanon |
| `SYR` | 叙利亚 | Syria |

### 阿拉伯（18）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ADE` | 亚丁 | Aden |
| `ALH` | 哈萨 | Haasa |
| `ANZ` | 阿尼扎 | Anizah |
| `ARB` | 阿拉伯 | Arabia |
| `DAW` | 代瓦西尔 | Dawasir |
| `HDR` | 哈德拉毛 | Hadramut |
| `HED` | 汉志 | Hejaz |
| `MDA` | 麦地那 | Medina |
| `MFL` | 米克利夫 | Mikhlaf |
| `MHR` | 迈赫拉 | Mahra |
| `NAJ` | 内志 | Najd |
| `NJR` | 奈季兰 | Najran |
| `OMA` | 阿曼 | Oman |
| `RAS` | 拉西 | Rassids |
| `SHM` | 舍迈尔 | Shammar |
| `SHR` | 沙迦 | Sharjah |
| `YAS` | 亚斯 | Yas |
| `YEM` | 也门 | Yemen |

### 埃及（3）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `EGY` | 埃及 | Egypt |
| `MAK` | 马库里亚 | Makuria |
| `MAM` | 马穆鲁克 | Mamluks |

### 波斯（21）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ARD` | 阿达兰 | Ardalan |
| `ARL` | 阿尔达比勒 | Ardabil |
| `BHT` | 索兰 | Soran |
| `BPI` | 比阿普斯 | Biapas |
| `ERS` | 埃兰沙赫尔 | Eranshahr |
| `FRS` | 法尔斯 | Fars |
| `ILK` | 伊利汗国 | Ilkhanate |
| `ISF` | 伊斯法罕 | Isfahan |
| `KHO` | 呼罗珊 | Khorasan |
| `KRM` | 克尔曼 | Kerman |
| `KRY` | 吉兰 | Gilan |
| `LRI` | 洛雷斯坦 | Luristan |
| `MGR` | 马拉盖 | Maregheh |
| `MSY` | 穆沙沙 | Mushasha |
| `ORM` | 霍尔木兹 | Hormuz |
| `PER` | 波斯 | Persia |
| `QAR` | 黑羊 | Qara Qoyunlu |
| `QOM` | 阿贾姆 | Ajam |
| `TAB` | 马赞德兰 | Mazandaran |
| `TBR` | 大不里士 | Tabriz |
| `YZD` | 亚兹德 | Yazd |

### 呼罗珊（3）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AFG` | 阿富汗 | Afghanistan |
| `BAL` | 俾路支斯坦 | Baluchistan |
| `SIS` | 锡斯坦 | Sistan |

### 高加索（9）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ARM` | 亚美尼亚 | Armenia |
| `AVR` | 阿瓦尔 | Avaria |
| `CIR` | 切尔克西亚 | Circassia |
| `GAZ` | 加齐库穆赫 | Gazikumukh |
| `GEO` | 格鲁吉亚 | Georgia |
| `IME` | 伊梅列季 | Imereti |
| `MLK` | 卡拉巴赫 | Karabakh |
| `SME` | 萨姆茨赫 | Samtskhe |
| `SRV` | 希尔凡 | Shirvan |

---

## 北非区域（77）

### 马格里布（15）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ALG` | 阿尔及尔 | Algiers |
| `FEZ` | 非斯 | Fez |
| `FZA` | 费赞 | Fezzan |
| `GHD` | 杰里德 | Djerid |
| `KBA` | 卡比利亚 | Kabylia |
| `MOR` | 摩洛哥 | Morocco |
| `MRK` | 马拉喀什 | Marrakesh |
| `MZB` | 姆扎卜 | Mzab |
| `SOS` | 苏斯 | Sus |
| `TET` | 得土安 | Tétouan |
| `TFL` | 塔菲拉勒特 | Tafilalt |
| `TGT` | 图古尔特 | Touggourt |
| `TLC` | 特莱姆森 | Tlemcen |
| `TRP` | 的黎波里 | Tripoli |
| `TUN` | 突尼斯 | Tunis |

### 萨赫勒（8）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AIR` | 阿伊尔 | Air |
| `DAR` | 达尔富尔 | Darfur |
| `KBO` | 卡奈姆-博尔努 | Kanem Bornu |
| `SON` | 桑海 | Songhai |
| `TMB` | 廷巴克图 | Timbuktu |
| `WAD` | 瓦达伊 | Wadai |
| `YAO` | 亚奥 | Yao |
| `ZAF` | 马西纳 | Macina |

### 尼日尔（22）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ASH` | 阿散蒂 | Ashanti |
| `BON` | 博诺曼 | Bonoman |
| `DAH` | 达荷美 | Dahomey |
| `DGB` | 达格邦 | Dagbon |
| `FUL` | 富洛 | Fulo |
| `GUR` | 法达恩古尔马 | Fada N'gourma |
| `HAU` | 豪萨 | Hausa |
| `JNN` | 杰内 | Jenné |
| `KAN` | 卡诺 | Kano |
| `KNG` | 孔 | Kong |
| `KTS` | 卡齐纳 | Katsina |
| `MAL` | 马里 | Mali |
| `MSI` | 莫西 | Mossi |
| `NUP` | 努佩 | Nupe |
| `OYO` | 奥约 | Oyo |
| `SOF` | 塞古 | Segu |
| `SOK` | 索科托 | Sokoto |
| `TEN` | 滕科多戈 | Tenkodogo |
| `WGD` | 瓦加杜古 | Wagadugu |
| `YAT` | 雅滕加 | Yatenga |
| `ZND` | 赞多马 | Zandoma |
| `ZZZ` | 扎造 | Zazzau |

### 几内亚（3）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BEN` | 贝宁 | Benin |
| `JOL` | 卓洛夫 | Jolof |
| `KBU` | 卡布 | Kaabu |

### 非洲之角（29）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ABB` | 栋古拉 | Dongola |
| `ADA` | 阿达尔 | Adal |
| `AFA` | 奥萨 | Aussa |
| `AJU` | 阿朱兰 | Ajuuraan |
| `AKS` | 阿克苏姆 | Aksum |
| `ALO` | 阿洛迪亚 | Alodia |
| `BEJ` | 贝扎 | Beja |
| `BTI` | 塞米恩 | Semien |
| `DAM` | 达莫特 | Damot |
| `ENA` | 伊那瑞亚 | Ennarea |
| `ETH` | 埃塞俄比亚 | Ethiopia |
| `GLE` | 格勒迪 | Geledi |
| `HAR` | 哈勒尔 | Harar |
| `HDY` | 哈迪亚 | Hadiya |
| `HOB` | 霍比奥 | Hobyo |
| `JIM` | 吉马 | Jimma |
| `JJI` | 詹吉罗 | Janjiro |
| `KAF` | 咖法 | Kaffa |
| `MDI` | 摩加迪沙 | Mogadishu |
| `MED` | 梅德利巴赫里 | Medri Bahri |
| `MJE` | 马吉尔廷 | Majeerteen |
| `MRE` | 马雷汉 | Marehan |
| `NBI` | 努比亚 | Nubia |
| `NUB` | 丰吉 | Funj |
| `OGD` | 欧加登 | Ogaadeen |
| `SOA` | 绍阿 | Shewa |
| `SOM` | 索马里 | Somalia |
| `WAR` | 瓦尔桑盖利 | Warsangali |
| `WLY` | 瓦莱提 | Welayta |

---

## 南非区域（43）

### 东非（14）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ANT` | 安泰莫罗 | Antemoro |
| `BTS` | 贝齐米萨拉卡 | Betsimisaraka |
| `LDU` | 隆杜 | Lundu |
| `LIB` | 利贝塔蒂亚 | Libertatia |
| `MBA` | 蒙巴萨 | Mombasa |
| `MFY` | 马哈法利 | Mahafaly |
| `MIR` | 梅里纳 | Imerina |
| `MKU` | 马库阿 | Makua |
| `MLI` | 马林迪 | Malindi |
| `MRA` | 马拉维 | Maravi |
| `PTE` | 帕泰 | Pate |
| `SKA` | 萨卡拉瓦 | Sakalava |
| `TBK` | 通布卡 | Tumbuka |
| `ZAN` | 基尔瓦 | Kilwa |

### 刚果（8）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `KON` | 刚果 | Kongo |
| `KSJ` | 卡桑吉 | Kasanje |
| `LND` | 隆达 | Lunda |
| `LOA` | 卢安果 | Loango |
| `NDO` | 恩东戈 | Ndongo |
| `SYO` | 索约 | Soyo |
| `TYO` | 特约 | Tyo |
| `YAK` | 雅卡 | Yaka |

### 南非（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `GZI` | 津巴布韦 | Zimbabwe |
| `RZI` | 罗兹维帝国 | Rozwi Empire |
| `RZW` | 布图阿 | Butua |
| `SFA` | 索法拉 | Sofala |
| `ZIM` | 穆塔帕 | Mutapa |
| `ZUL` | 祖鲁 | Zulu |

### 中非（15）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BNY` | 布尼奥罗 | Bunyoro |
| `BSG` | 布索加 | Busoga |
| `BUG` | 布干达 | Buganda |
| `BUU` | 布隆迪 | Burundi |
| `CKW` | 绍奎 | Chokwe |
| `KIK` | 基孔贾 | Kikondja |
| `KIT` | 基塔拉 | Kitara |
| `KLD` | 卡隆兑 | Kalundwe |
| `KRW` | 卡拉圭 | Karagwe |
| `KUB` | 库巴 | Kuba |
| `KZB` | 卡曾贝 | Kazembe |
| `LUB` | 卢巴 | Luba |
| `NKO` | 安科莱 | Nkore |
| `RWA` | 卢旺达 | Rwanda |
| `UBH` | 布哈 | Buha |

---

## 印度大区（104）

### 印度斯坦（34）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BGL` | 巴克尔根德 | Baghelkhand |
| `BHA` | 婆罗多 | Bharat |
| `BND` | 本德尔肯德 | Bundelkhand |
| `DLH` | 德里 | Delhi |
| `DNG` | 丹格 | Dang |
| `DTI` | 多提 | Doti |
| `GHR` | 加瓦尔 | Garhwal |
| `GRK` | 廓尔喀 | Gorkha |
| `GWA` | 瓜廖尔 | Gwalior |
| `HAD` | 哈多提 | Hadoti |
| `HIN` | 印度斯坦 | Hindustan |
| `JML` | 久姆拉 | Jumla |
| `JNP` | 章普尔 | Jaunpur |
| `KGR` | 冈格拉 | Kangra |
| `KLP` | 迦尔毗 | Kalpi |
| `KMN` | 库马翁 | Kumaon |
| `KSH` | 克什米尔 | Kashmir |
| `KTU` | 加德满都 | Kathmandu |
| `LDK` | 拉达克 | Ladakh |
| `LWA` | 林布旺 | Limbuwan |
| `MKP` | 马克万普尔 | Makwanpur |
| `MUG` | 莫卧儿 | Mughals |
| `MUL` | 木尔坦 | Multan |
| `NPL` | 尼泊尔 | Nepal |
| `ODH` | 奥德 | Oudh |
| `PAN` | 卡林贾尔 | Kalinjar |
| `PTA` | 伯蒂亚拉 | Patiala |
| `PUN` | 旁遮普 | Punjab |
| `RJP` | 拉杰普塔纳 | Rajputana |
| `RMP` | 罗希尔坎德 | Rohilkhand |
| `SRG` | 苏古贾 | Surguja |
| `SRH` | 西尔欣德 | Sirhind |
| `SRM` | 色姆尔 | Sirmur |
| `TRT` | 蒂鲁德 | Tirhut |

### 孟加拉（21）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ASS` | 阿萨姆 | Assam |
| `BNG` | 孟加拉 | Bengal |
| `BST` | 巴斯塔 | Bastar |
| `EIC` | 东印度公司 | East India Company |
| `GRJ` | 迦贾德 | Garjat |
| `JPR` | 杰伊普尔 | Jeypore |
| `KAC` | 卡恰尔 | Kachar |
| `KJH` | 凯翁贾尔 | Keonhjar |
| `KLH` | 卡拉汉迪 | Kalahandi |
| `KMT` | 科奇 | Koch |
| `MBL` | 毗湿奴普尔 | Bishnupur |
| `MLB` | 曼尼普尔 | Manipur |
| `NGP` | 贾坎德 | Jharkhand |
| `ORI` | 奥里萨 | Orissa |
| `PRD` | 帕拉克米迪 | Parlakhimidi |
| `PTT` | 巴特那 | Patna |
| `RTT` | 拉坦普尔 | Ratanpur |
| `SBP` | 萨姆巴尔普尔 | Sambalpur |
| `SDY` | 萨地亚 | Sadiya |
| `TPR` | 特里普拉 | Tripura |
| `VOC` | 联合东印度公司 | Vereenigde Oostindische Compagnie |

### 西印度（22）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BDA` | 巴罗达 | Baroda |
| `BGA` | 巴格拉纳 | Baglana |
| `CMP` | 雷瓦坎塔 | Rewa Kantha |
| `DHU` | 敦达尔 | Dhundhar |
| `GUJ` | 古吉拉特 | Gujarat |
| `IDR` | 伊达尔 | Idar |
| `JAN` | 禅伽罗 | Jangladesh |
| `JGD` | 朱纳格特 | Junagarh |
| `JLV` | 恰拉瓦尔 | Jhalavad |
| `JSL` | 斋沙默尔 | Jaisalmer |
| `KAT` | 卡奇 | Kutch |
| `KHD` | 坎德什 | Khandesh |
| `MAW` | 马尔瓦尔 | Marwar |
| `MER` | 梅瓦尔 | Mewar |
| `MEW` | 梅瓦特 | Mewat |
| `MLW` | 摩腊婆 | Malwa |
| `NGA` | 纳高尔 | Nagaur |
| `NVR` | 纳瓦那加 | Navanagar |
| `PRB` | 博尔本德尔 | Porbandar |
| `PTL` | 巴利塔纳 | Palitana |
| `RJK` | 拉杰果德 | Rajkot |
| `SND` | 信德 | Sindh |

### 德干（19）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AHM` | 艾哈迈德纳格尔 | Ahmednagar |
| `BAH` | 巴赫曼尼 | Bahmanis |
| `BIJ` | 比贾布尔 | Bijapur |
| `BRR` | 贝拉尔 | Berar |
| `CHD` | 昌达 | Chanda |
| `DEC` | 德干 | Deccan |
| `GDW` | 加哈 | Garha |
| `GOC` | 戈尔孔达 | Golkonda |
| `JAJ` | 哈卜尚 | Habsan |
| `KLN` | 开拉迪 | Keladi |
| `KLT` | 科拉舒纳德 | Kolathunad |
| `KOC` | 科钦 | Kochin |
| `MAB` | 卡利卡特 | Calicut |
| `MAR` | 马拉塔 | Marathas |
| `MYS` | 迈索尔 | Mysore |
| `NAG` | 那格浦尔 | Nagpur |
| `TLG` | 特伦甘纳 | Telingana |
| `VIJ` | 毗奢耶那伽罗 | Vijayanagar |
| `VND` | 维纳德 | Venad |

### 科罗曼德尔（8）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CEY` | 科特 | Kotte |
| `GNG` | 京吉 | Gingee |
| `JFN` | 贾夫纳 | Jaffna |
| `KND` | 康提 | Kandy |
| `KRK` | 卡纳提克 | Carnatic |
| `MAD` | 马杜赖 | Madurai |
| `TNJ` | 坦焦尔 | Tanjore |
| `YOR` | 安得拉 | Andhra |

---

## 东印度大区（78）

### 缅甸（13）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ARK` | 阿拉干 | Arakan |
| `AVA` | 阿瓦 | Ava |
| `BPR` | 卑谬 | Prome |
| `HSE` | 兴威 | Hsenwi |
| `HSI` | 昔卜 | Hsipaw |
| `KAL` | 格礼 | Kale |
| `MKA` | 孟拱 | Mong Kawng |
| `MNI` | 孟乃 | Mong Nai |
| `MPA` | 孟拜 | Mong Pai |
| `MYA` | 孟养 | Mong Yang |
| `PEG` | 勃固 | Pegu |
| `SST` | 掸邦 | Shan |
| `TAU` | 东吁 | Taungu |

### 马来（19）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ATJ` | 亚齐 | Aceh |
| `BRS` | 巴鲁斯 | Barus |
| `DGL` | 马尔代夫 | Maldives |
| `DLI` | 碟里 | Deli |
| `IND` | 因陀罗补罗 | Indrapura |
| `JMB` | 占碑 | Jambi |
| `JOH` | 柔佛 | Johor |
| `KED` | 吉打 | Kedah |
| `KEL` | 吉兰丹 | Kelantan |
| `LIG` | 洛坤 | Ligor |
| `MLC` | 马六甲 | Malacca |
| `MSA` | 马来亚 | Malaya |
| `PAH` | 彭亨 | Pahang |
| `PAT` | 北大年 | Pattani |
| `PGR` | 帕迦鲁荣 | Pagarruyung |
| `PLB` | 巴邻旁 | Palembang |
| `PRK` | 霹雳 | Perak |
| `PSA` | 八昔 | Pasai |
| `SAK` | 锡亚克 | Siak |

### 摩鹿加（15）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BNE` | 波尼 | Bone |
| `BTN` | 布敦 | Buton |
| `BTU` | 武端 | Butuan |
| `CEB` | 宿务 | Cebu |
| `LNO` | 拉瑙 | Lanao |
| `LUW` | 鲁乌 | Luwu |
| `MAS` | 马加斯 | Madyas |
| `MGD` | 马京达瑙 | Maguindanao |
| `MKS` | 望加锡 | Makassar |
| `MNA` | 马尼拉 | Maynila |
| `PGS` | 邦阿西楠 | Pangasinan |
| `SUL` | 苏禄 | Sulu |
| `TDO` | 汤都 | Tondo |
| `TER` | 特尔纳特 | Ternate |
| `TID` | 蒂多雷 | Tidore |

### 印度尼西亚（14）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BAN` | 万丹 | Banten |
| `BEI` | 文莱 | Brunei |
| `BEU` | 伯劳 | Berau |
| `BLI` | 巴厘 | Bali |
| `BLM` | 布兰邦岸 | Blambangan |
| `BNJ` | 班贾尔 | Banjar |
| `CRB` | 井里汶 | Cirebon |
| `DMK` | 淡目 | Demak |
| `KUT` | 古泰 | Kutai |
| `LFA` | 兰芳 | Lanfang |
| `MAJ` | 满者伯夷 | Majapahit |
| `MTR` | 马塔兰 | Mataram |
| `SMB` | 三发 | Sambas |
| `SUN` | 巽他 | Sunda |

### 中南半岛（17）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ANN` | 安南 | Annam |
| `AYU` | 阿瑜陀耶 | Ayutthaya |
| `CHA` | 占婆 | Champa |
| `CHK` | 占巴塞 | Champasak |
| `DAI` | 大越 | Dai Viet |
| `JAR` | 嘉莱 | Jarai |
| `KHM` | 高棉 | Khmer |
| `KOH` | 格贺 | Koho |
| `LNA` | 兰纳 | Lan Na |
| `LUA` | 琅勃拉邦 | Luang Prabang |
| `LXA` | 澜沧 | Lan Xang |
| `MPH` | 孟潘 | Muang Phuan |
| `RHA` | 埃地 | Rhade |
| `SIA` | 暹罗 | Siam |
| `SUK` | 素可泰 | Sukhothai |
| `TOK` | 东京 | Tonkin |
| `VIE` | 万象 | Vientiane |

---

## 大洋洲大区（35）

### 大洋洲（19）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AOT` | 奥特亚罗瓦 | Aotearoa |
| `HAW` | 夏威夷 | Hawai'i |
| `KAA` | 考爱 | Kaua'i |
| `LAI` | 劳 | Lau |
| `MAA` | 雅提阿瓦 | Ngati Awa |
| `MAU` | 毛伊 | Maui |
| `OAH` | 瓦胡 | O'ahu |
| `SAM` | 萨摩亚 | Samoa |
| `TAK` | 雅提卡胡伍努 | Ngati Kahungunu |
| `TAN` | 泰努伊 | Tainui |
| `TEA` | 雅提拉宜努伊 | Ngati Ranginui |
| `TNK` | 雅提托阿 | Ngati Toa |
| `TOG` | 汤加 | Tonga |
| `TTT` | 雅普希 | Ngapuhi |
| `UHW` | 夏威夷 | Hawai'i |
| `VIL` | 维提 | Viti Levu |
| `VIT` | 斐济 | Viti |
| `VNL` | 瓦努阿 | Vanua Levu |
| `WAI` | 怀塔哈 | Waitaha |

### 澳大利亚（16）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AUS` | 澳大利亚 | Australia |
| `AWN` | 阿翁提姆 | Awngthim |
| `EOR` | 约拉 | Eora |
| `GMI` | 卡米勒罗伊 | Kamilaroi |
| `KAU` | 高纳 | Kaurna |
| `KUL` | 库林 | Kulin |
| `LAR` | 拉拉基亚 | Larrakia |
| `MIA` | 米安金 | Mianjin |
| `MLG` | 马尔加纳 | Malgana |
| `NOO` | 农雅 | Nyoongah |
| `NZL` | 西兰蒂亚 | Zealandia |
| `PLW` | 帕拉瓦 | Palawa |
| `TIW` | 提维 | Tiwi |
| `WRU` | 伍伦杰里 | Wurundjeri |
| `YNU` | 亚努瓦 | Yanuwa |
| `YOL` | 雍古 | Yolngu |

---

## 北美大区（96）

### 哈德逊湾（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ASI` | 阿西尼博因 | Assiniboine |
| `BLA` | 黑脚 | Blackfoot |
| `CHY` | 夏延 | Cheyenne |
| `NAK` | 纳卡韦 | Nakawe |
| `NEH` | 内希亚乌 | Nehiyaw |
| `WCR` | 克里 | Cree |

### 卡斯卡迪亚（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ALA` | 阿拉斯加 | Alaska |
| `CNK` | 奇努克 | Chinook |
| `CSC` | 卡斯卡迪亚 | Cascadia |
| `HDA` | 海达 | Haida |
| `SAL` | 萨利什 | Salish |
| `SHO` | 肖肖尼 | Shoshone |

### 大平原（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ARP` | 阿拉帕霍 | Arapaho |
| `COM` | 科曼奇 | Comanche |
| `KIO` | 基奥瓦 | Kiowa |
| `LAK` | 拉科塔 | Lakota |
| `PAW` | 波尼 | Pawnee |
| `WCY` | 维奇耶纳 | Wichiyena |

### 密西西比（18）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ABI` | 阿比卡 | Abihka |
| `ANL` | 阿尼尔科 | Anilco |
| `ATA` | 阿塔哈奇 | Atahachi |
| `CAD` | 卡多 | Caddo |
| `CAQ` | 卡斯基 | Casqui |
| `CCA` | 奇斯卡 | Chisca |
| `CHI` | 奇克索 | Chickasaw |
| `CHO` | 乔克托 | Choctaw |
| `COW` | 考维塔 | Coweta |
| `CRE` | 克里克 | Creek |
| `FLO` | 佛罗里达 | Florida |
| `HWK` | 哈萨韦凯拉 | Hathawekela |
| `KSP` | 基斯波科 | Kispoko |
| `LOU` | 路易斯安那 | Louisiana |
| `NTC` | 纳基托什 | Natchitoches |
| `NTZ` | 纳奇兹 | Natchez |
| `PCH` | 帕卡哈 | Pacaha |
| `QUI` | 基斯基斯 | Quizquiz |

### 北美东南（12）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ALT` | 奥尔塔马霍 | Altamaha |
| `CHE` | 切罗基 | Cherokee |
| `CIA` | 奇亚哈 | Chiaha |
| `COF` | 科菲塔切基 | Cofitachequi |
| `COO` | 库萨 | Coosa |
| `ETO` | 埃托瓦 | Etowah |
| `ICH` | 伊奇西 | Ichisi |
| `JOA` | 乔阿拉 | Joara |
| `KSI` | 卡西塔 | Kasihta |
| `POW` | 波瓦坦 | Powhatan |
| `SAT` | 萨塔波 | Satapo |
| `TSC` | 塔斯卡罗拉 | Tuscarora |

### 北美东北（17）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ABE` | 阿布纳基 | Abenaki |
| `CAY` | 卡尤加 | Cayuga |
| `ERI` | 伊利 | Erie |
| `IRO` | 易洛魁 | Iroquois |
| `LEN` | 莱纳佩 | Lenape |
| `MAH` | 莫希干 | Mahican |
| `MOH` | 莫霍克 | Mohawk |
| `ONE` | 奥奈达 | Oneida |
| `ONO` | 奥农多加 | Onondaga |
| `PEN` | 佩诺布斯科特 | Penobscot |
| `PEQ` | 佩科特 | Pequot |
| `SEN` | 塞尼卡 | Seneca |
| `SUS` | 萨斯奎汉诺克 | Susquehannock |
| `USA` | 美利坚 | United States |
| `VRM` | 佛蒙特 | Vermont |
| `WAM` | 万帕诺亚格 | Wampanoag |
| `WEN` | 文罗 | Wenro |

### 五大湖（14）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CAO` | 卡霍基亚 | Cahokia |
| `CLG` | 查拉高萨 | Chalaghawtha |
| `FOX` | 福克斯 | Fox |
| `ILI` | 伊利诺伊 | Illinois |
| `ILL` | 伊利尼维克 | Illiniwek |
| `KSK` | 卡斯卡斯基亚 | Kaskaskia |
| `MMI` | 迈阿密 | Miami |
| `OEO` | 奥内奥塔 | Oneota |
| `OJI` | 奥吉布瓦 | Ojibwe |
| `OSA` | 欧塞奇 | Osage |
| `PEO` | 皮奥里亚 | Peoria |
| `POT` | 波塔瓦托米 | Potawatomi |
| `SHA` | 肖尼 | Shawnee |
| `SIO` | 苏族 | Sioux |

### 加拿大（17）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AGG` | 阿蒂格内农纳哈克 | Attigneenongnahac |
| `AGQ` | 阿尔冈昆 | Algonquin |
| `ARN` | 阿伦达罗嫩 | Arendaronon |
| `ATT` | 阿蒂格纳万坦 | Attignawantan |
| `ATW` | 阿蒂万达伦 | Attiwandaron |
| `CAN` | 加拿大 | Canada |
| `HUR` | 休伦 | Huron |
| `INN` | 因努 | Innu |
| `MIK` | 米克马克 | Mikmaq |
| `MLS` | 马勒西特 | Maliseet |
| `MSG` | 米西索加 | Mississage |
| `OSH` | 奥谢阿加 | Osheaga |
| `OTT` | 渥太华 | Ottawa |
| `QUE` | 魁北克 | Quebec |
| `STA` | 斯塔达科纳 | Stadacona |
| `TAH` | 塔洪塔恩拉特 | Tahontaenrat |
| `TIO` | 提奥嫩塔特 | Tionontate |

---

## 中南美区域（86）

### 中美洲（13）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CAM` | 中美洲联邦 | United Central America |
| `CHT` | 乔尔蒂 | Chorti |
| `CNP` | 坎佩奇 | Can Pech |
| `COC` | 科科姆 | Cocomes |
| `CTM` | 查克特马尔 | Chactemal |
| `ITZ` | 伊察 | Itza |
| `KAQ` | 卡克奇克尔 | Kaqchikel |
| `KIC` | 基切 | Kiche |
| `LAC` | 乔齐尔 | Tzotzil |
| `MAY` | 玛雅 | Maya |
| `MIS` | 米斯基托 | Miskito |
| `XIU` | 休 | Xiu |
| `YOK` | 约科坦 | Yokotan |

### 墨西哥（18）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `AZT` | 阿兹特克 | Aztec |
| `CCM` | 奇奇梅克 | Chichimeca |
| `CLM` | 科利马 | Colima |
| `COI` | 科伊斯特拉瓦卡 | Coixtlahuaca |
| `GAM` | 瓜马尔 | Guamar |
| `HST` | 瓦斯特克 | Huastec |
| `MAT` | 马特拉钦卡 | Matlatzinca |
| `MEX` | 墨西哥 | Mexico |
| `MIX` | 米斯特克 | Mixtec |
| `OTO` | 奥托米 | Otomi |
| `TAR` | 普雷佩查 | Purépecha |
| `TEO` | 特奥蒂特兰 | Teotitlan |
| `TLA` | 特拉帕内克 | Tlapanec |
| `TLX` | 特拉斯卡拉 | Tlaxcala |
| `TON` | 托纳拉 | Tonala |
| `TOT` | 托托纳克 | Totonac |
| `XAL` | 哈利斯科 | Xalisco |
| `ZAP` | 萨波特克 | Zapotec |

### 加勒比（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CUB` | 古巴 | Cuba |
| `HAT` | 海地 | Haiti |
| `NSS` | 新普罗维登斯 | New Providence |
| `PRY` | 皇家港 | Port Royal |
| `TOR` | 托尔图加 | Tortuga |
| `WSI` | 西印度 | West Indies |

### 里奥格兰德（5）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `HNI` | 哈西奈 | Hasinai |
| `LIP` | 利潘 | Lipan |
| `MSC` | 梅斯卡莱罗 | Mescalero |
| `TEX` | 得克萨斯 | Texas |
| `WIC` | 威奇托 | Wichita |

### 加利福尼亚（13）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ACO` | 阿科马 | Acoma |
| `APA` | 阿帕奇 | Apache |
| `CAL` | 加利福尼亚 | California |
| `ISL` | 伊斯莱塔 | Isleta |
| `KER` | 齐亚 | Zia |
| `NAH` | 纳瓦霍 | Navajo |
| `OHK` | 奥凯奥温盖 | Ohkay Owingeh |
| `PIM` | 皮马 | Pima |
| `PUE` | 普韦布洛 | Pueblo |
| `SNA` | 索诺拉 | Sonora |
| `YAQ` | 亚基 | Yaqui |
| `YKT` | 约库特 | Yokuts |
| `ZNI` | 祖尼 | Zuni |

### 巴西（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `BRZ` | 巴西 | Brazil |
| `GUA` | 瓜拉尼 | Guarani |
| `PTG` | 波蒂瓜拉 | Potiguara |
| `TPA` | 图皮南巴 | Tupinamba |
| `TPQ` | 图皮尼金 | Tupiniquim |
| `TUA` | 塔普亚 | Tapuia |

### 哥伦比亚（6）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `ARW` | 阿拉瓦克 | Arawak |
| `CAB` | 加勒比 | Carib |
| `COL` | 哥伦比亚 | Colombia |
| `MCA` | 穆伊斯卡 | Muisca |
| `TAI` | 泰罗纳 | Tairona |
| `VNZ` | 委内瑞拉 | Venezuela |

### 秘鲁（12）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CHM` | 奇穆 | Chimu |
| `CJA` | 卡哈马卡 | Cajamarca |
| `CLA` | 科拉 | Colla |
| `CSU` | 库斯科 | Cuzco |
| `CYA` | 查查波亚 | Chachapoya |
| `HJA` | 胡伊拉 | Huyla |
| `ICM` | 依其马 | Ichma |
| `INC` | 印加 | Inca |
| `PCJ` | 帕卡赫斯 | Pacajes |
| `PEU` | 秘鲁 | Peru |
| `QTO` | 基多 | Quito |
| `WKA` | 万卡 | Wanka |

### 上秘鲁（3）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CCQ` | 查尔查奇 | Calchaqui |
| `CRA` | 查卡 | Charca |
| `PRG` | 巴拉圭 | Paraguay |

### 拉普拉塔（4）

| TAG | 中文国名 | 英文原名 |
|---|---|---|
| `CHL` | 智利 | Chile |
| `CUA` | 查鲁亚 | Charrua |
| `LAP` | 拉普拉塔 | La Plata |
| `MPC` | 马普切 | Mapuche |

---

## 特殊标签（无地理归属）

| TAG | 中文名 | 英文名 |
|---|---|---|
| `NAT` | 原住民 | Natives |
| `PIR` | 海盗 | Pirates |
| `REB` | 叛军 | Rebels |
