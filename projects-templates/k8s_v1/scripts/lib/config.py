app_name = "k8s_v1_scripts"
version = "1.0.0"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    ID_ERROR,
) = range(4)

ERRORS = {
    DIR_ERROR: "config directory error",
    FILE_ERROR: "config file error",
    ID_ERROR: "id error",
}
