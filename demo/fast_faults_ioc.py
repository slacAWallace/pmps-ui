#!/usr/bin/env python3
import itertools
import random
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run


class FastFaultsIOC(PVGroup):
    async def my_read(self, instance):
        await instance.write(bool(random.randint(0, 100)%2))
        return instance.value

    beam_permitted_rbv = pvproperty(name='BeamPermitted_RBV', value=True)
    info_string_rbv = pvproperty(name='InfoString_RBV', value='Arbiter.ArbiterPLC.Testing.testFF;TRUE;0;Test Name;Test Description;FALSE;')
    ok_rbv = pvproperty(name='OK_RBV', dtype=bool, get=my_read)
    reset = pvproperty(name='Reset', value=False)
    reset_rbv = pvproperty(name='Reset_RBV', value=False)
    ovrd_activate = pvproperty(name='Ovrd:Activate', value=False)
    ovrd_activate_rbv = pvproperty(name='Ovrd:Activate_RBV', dtype=bool, get=my_read)
    ovrd_active_rbv = pvproperty(name='Ovrd:Active_RBV', dtype=bool, get=my_read)
    ovrd_deactivate = pvproperty(name='Ovrd:Deactivate', value=False)
    ovrd_deactivate_rbv = pvproperty(name='Ovrd:Deactivate_RBV', value=False)
    ovrd_duration = pvproperty(name='Ovrd:Duration', value=0)
    ovrd_duration_rbv = pvproperty(name='Ovrd:Duration_RBV', value=0)
    ovrd_elapsedtime_rbv = pvproperty(name='Ovrd:ElapsedTime_RBV', value=0)


class PreemptiveRequests(PVGroup):
    key_rbv = pvproperty(name='Key_RBV', value=1000)
    rate_rbv = pvproperty(name='Rate_RBV', value=120, units='Hz')
    attenuation_rbv = pvproperty(name='Attenuation_RBV', value=100.0,
                                 units='%')
    photon_energy_ranges_rbv = pvproperty(name='PhotonEnergyRanges_RBV',
                                          value=1023, dtype=int)
    pulse_energy_rbv = pvproperty(name='PulseEnergy_RBV', value=10, units='mJ')

    cohort_rbv = pvproperty(name='Cohort_RBV', value=9999)
    valid_rbv = pvproperty(name='Valid_RBV', value=True)


class BeamParametersIOC(PVGroup):
    attenuation_rbv = pvproperty(name='Attenuation_RBV', value=100.0, units='%')
    pulse_energy_rbv = pvproperty(name='PulseEnergy_RBV', value=10, units='mJ')
    rate_rbv = pvproperty(name='Rate_RBV', value=120, units='Hz')


class CurrentBP(BeamParametersIOC):
    photon_energy_ranges_rbv = pvproperty(name='PhotonEnergyRanges_RBV', value=3903, dtype=int)


class RequestedBP(BeamParametersIOC):
    photon_energy_ranges_rbv = pvproperty(name='PhotonEnergyRanges_RBV', value=1023, dtype=int)


class IOCMain(PVGroup):
    ev_rangecnst_rbv = pvproperty(name='eVRangeCnst_RBV', value=[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7])
    spectrogram = pvproperty(name='spectrogram', value=[0.8, 0.9, 1, 1.1, 1, 1.2, 1, 1, 1, 1, 1.2, 2.2, 1.2, 1.1, 1.05, 1.05, 1.08, 1.2, 1.08, 1.05, 1.05, 1.05, 1.04, 1.06, 1.08, 1.2, 1.5, 1.8, 2, 2.4, 2.8, 3, 2.98, 2.94, 2.8, 2.4, 2, 1.8, 1.5, 1.2, 1.08, 0.9])

    beam_class_channel = pvproperty(name="BeamClassOutputs:BeamClassChannel_RBV", value=85)
    clts_channel = pvproperty(
        name="CuRateOutputs:CTLSChannel_RBV", value=4)

    def __init__(self, prefix, **kwargs):
        super().__init__(prefix, **kwargs)


def create_ffs(ioc, prefix, ffos=2, ffs=50):
    groups = {}
    ffos_zfill = len(str(ffos)) + 1
    ffs_zfill=len(str(ffs))+1

    entries = itertools.product(range(1, ffos+1), range(1, ffs+1))
    for ffo, ff in entries:
        s_ffo = str(ffo).zfill(ffos_zfill)
        s_ff = str(ff).zfill(ffs_zfill)
        g_prefix = f'{prefix}FFO:{s_ffo}:FF:{s_ff}:'
        groups[g_prefix] = FastFaultsIOC(g_prefix)

    for group in groups.values():
        ioc.pvdb.update(**group.pvdb)


def create_preemptive_requests(ioc, prefix, arbiter, pool_start=0, pool_end=20):
    groups = {}
    pool_zfill = len(str(pool_end)) + 1

    entries = range(pool_start, pool_end+1)
    for pool in entries:
        g_prefix = f'{prefix}{arbiter}:AP:Entry:{str(pool).zfill(pool_zfill)}:'
        groups[g_prefix] = PreemptiveRequests(g_prefix)

    for group in groups.values():
        ioc.pvdb.update(**group.pvdb)


def create_beam_parameters(ioc, prefix):
    parameters = {}
    for itm, cls in [('CurrentBP:', CurrentBP), ('RequestedBP:', RequestedBP)]:
        p_prefix = f'{prefix}{itm}'
        parameters[itm] = cls(p_prefix)

    for p in parameters.values():
        ioc.pvdb.update(**p.pvdb)


def create_ioc(prefix, **ioc_options):
    ioc = IOCMain(prefix=prefix, **ioc_options)
    create_beam_parameters(ioc, prefix)
    create_preemptive_requests(ioc, prefix, "Arbiter:01", 0, 20)
    create_ffs(ioc, prefix)

    return ioc


if __name__ == '__main__':
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='PMPS:LFE:',
        desc=IOCMain.__doc__,
    )

    ioc = create_ioc(**ioc_options)

    run(ioc.pvdb, **run_options)
