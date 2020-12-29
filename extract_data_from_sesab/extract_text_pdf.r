require("pdftools")
require("dplyr")

path_ = './boletins_sesab/'
raw_path = paste(path_, 'raw/', sep="")
refined_path = paste(path_, 'refined/', sep="")

last_file = sort(list.files(paste(path_, "last_boletim/", sep="")), decreasing = T)[1]
date_base = unlist(last_file %>% strsplit("_"))
date_base = substr(date_base[length(date_base)], 1, 8)
date_base = paste(substr(date_base, 5, 8), substr(date_base, 3, 4), substr(date_base, 1, 2), sep = "-")

pages_path = paste(refined_path, date_base, "/01_extract/", sep="")

f = pdf_text(paste(raw_path, last_file, sep=""))
# f = f %>% strsplit(split = "\n")

dir.create(pages_path, recursive = T, showWarnings = F)
write.table(f, paste(pages_path, "01_boletim.txt", sep=""))

# for(i in 1:length(f)) {
#   if (i < 10)  write.table(f[i], paste(pages_path, "boletim_pg0", i, ".txt", sep=""), row.names = F)
#   else  write.table(f[i], paste(pages_path, "boletim_pg", i, ".txt", sep=""), row.names = F)
# }
