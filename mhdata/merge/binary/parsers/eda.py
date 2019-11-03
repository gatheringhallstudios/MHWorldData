from . import structreader as sr

class EdaBuildup(sr.AnnotatedStruct):
    base: sr.uint()
    buildup: sr.uint()
    max: sr.uint()
    timer_numerator: sr.float() 
    timer_denominator: sr.uint()
    duration: sr.float()
    decrease: sr.float()
    decrease_limit: sr.float()

class DttEda(sr.AnnotatedStruct):
    "Binary type for monster status info"
    filetype: sr.uint()
    monster_id: sr.uint()
    version: sr.byte()

    poison_buildup: EdaBuildup()
    poison_damageX2: sr.uint()
    poison_interval: sr.float()

    sleep_buildup: EdaBuildup()
    para_buildup: EdaBuildup()
    stun_buildup: EdaBuildup()

    exhaust_buildup: EdaBuildup()
    unk1: sr.uint()
    unk2: sr.float()

    mount_buildup: EdaBuildup()

    blast_buildup: EdaBuildup()
    blast_damage: sr.uint()

    tranq_buildup: EdaBuildup()
    unk3: sr.uint()

    flash_buildup: EdaBuildup()

    mount_knockdown_buildup: EdaBuildup()
    unk4: sr.uint()

    dung_buildup: EdaBuildup()
    unk5: sr.uint()
    unk6: sr.float()

    shock_trap_buildup: EdaBuildup()
    pitfall_trap_buildup: EdaBuildup()
    vine_trap_buildup: EdaBuildup()

    unk_status_buildup: EdaBuildup()
    elderseal_buildup: EdaBuildup()
    