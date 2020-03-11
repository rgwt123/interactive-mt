python translate_allnist.py --id ${1}

FILE=all_models/base/nistall_predict_${1}.en

P2S=/data2/twang/corpus/nist-zh2en

head -878 $FILE > ${P2S}/temp2
head -1797 $FILE | tail -919 > ${P2S}/temp3
head -3585 $FILE | tail -1788 > ${P2S}/temp4
head -4667 $FILE | tail -1082 > ${P2S}/temp5
head -6331 $FILE | tail -1664 > ${P2S}/temp6
head -7688 $FILE | tail -1357 > ${P2S}/temp8

for i in {2,3,4,5,6,8}
do
  $P2S/plain2sgm tst ${P2S}/temp${i} > ${P2S}/temp${i}.sgm
  $P2S/mteval-v11b.pl -r ${P2S}/ref${i}.sgm -s ${P2S}/src${i}.sgm -t ${P2S}/temp${i}.sgm | grep "BLEU score ="
done


