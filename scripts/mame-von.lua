-- Virtual-On focused MAME subtarget.
-- Keep this list deliberately small so driver iteration does not rebuild all MAME.

CPUS["I960"] = true
CPUS["ADSP2106X"] = true
CPUS["M68000"] = true
CPUS["Z80"] = true

SOUNDS["SCSP"] = true
SOUNDS["MULTIPCM"] = true

MACHINES["CXD1095"] = true
MACHINES["EEPROMDEV"] = true
MACHINES["MB8421"] = true
MACHINES["MSM6253"] = true

function createProjects_mame_von(_target, _subtarget)
	project("mame_von")
	targetsubdir(_target .. "_" .. _subtarget)
	kind(LIBTYPE)
	uuid(os.uuid("drv-mame-von"))
	addprojectflags()
	precompiledheaders_novs()

	includedirs {
		MAME_DIR .. "src/osd",
		MAME_DIR .. "src/emu",
		MAME_DIR .. "src/devices",
		MAME_DIR .. "src/mame/shared",
		MAME_DIR .. "src/lib",
		MAME_DIR .. "src/lib/util",
		MAME_DIR .. "3rdparty",
		GEN_DIR .. "mame/layout",
	}

	files {
		MAME_DIR .. "src/mame/sega/model2.cpp",
		MAME_DIR .. "src/mame/sega/model2_v.cpp",
		MAME_DIR .. "src/mame/sega/m2comm.cpp",
		MAME_DIR .. "src/mame/sega/model1io.cpp",
		MAME_DIR .. "src/mame/sega/model1io2.cpp",
		MAME_DIR .. "src/mame/sega/315_5296.cpp",
		MAME_DIR .. "src/mame/sega/315_5649.cpp",
		MAME_DIR .. "src/mame/sega/segaic24.cpp",
		MAME_DIR .. "src/mame/sega/segabill.cpp",
	}
end

function linkProjects_mame_von(_target, _subtarget)
	links {
		"mame_von",
	}
end
