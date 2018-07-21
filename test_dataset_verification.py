import dataset_verification as dataset

AUDIO_STORAGE_PATH = "/media/frisco/FAT/cross-modal/audios/"
AUDIO_SYNCED_STORAGE_PATH = "/media/frisco/FAT/cross-modal/synced_audios/"
NEW_AUDIO_SYNCED_STORAGE_PATH = "/media/frisco/FAT/cross-modal/doub_sync_audios/"

df = dataset.cleanup(AUDIO_STORAGE_PATH, AUDIO_SYNCED_STORAGE_PATH)
