import unittest
from pathlib import Path

from autoetl.project import ETLProject


class TestNewProject(unittest.TestCase):
    def test_create_project_object(self):
        project = ETLProject(
            name="Chirp Chirp Chirp 🐦",
            description="Don't worry about a thing, cause every little thing is gonna be alright",
            project_id="chirp",
        )
        self.assertIsInstance(project, ETLProject, msg="project is not a ETLProject")
        self.assertEqual(project.name, "Chirp Chirp Chirp 🐦")
        self.assertEqual(
            project.description,
            "Don't worry about a thing, cause every little thing is gonna be alright",
        )
        self.assertEqual(project.id, "chirp")

    def test_create_project_in_tmpdir(self):
        project = ETLProject(
            name="Rainy Day Project! 🌧️",
            description="Daily Weather data for all of my airbnb properties",
            fdir=None,
        )
        self.assertEqual(project.id, "rainy_day_project")
        self.assertIsInstance(project.fdir, Path)
        self.assertTrue(project.fdir.name.endswith(project.id))
        self.assertTrue(project.fdir.name.startswith("autoetl_"))
        self.assertTrue(
            project.fdir.exists(), msg="Temp Project directory should be created"
        )

    def test_create_project_in_cwd(self):
        project = ETLProject(
            name="Cloudy Day Project! ☁️",
            fdir="cwd",
        )
        self.assertEqual(project.id, "cloudy_day_project")
        self.assertIsInstance(project.fdir, Path)
        self.assertEqual(project.fdir.name, project.id)
        self.assertFalse(
            project.fdir.exists(), msg="Project directory should not exist yet"
        )

    def test_init_project(self):
        project = ETLProject(
            name="Sunny Day Project! ☀️",
        )
        self.assertIsInstance(project.fdir, Path)
        self.assertTrue(
            project.fdir.exists(), msg="Temp Project directory should be created"
        )
        project.init()
        self.assertTrue(
            project.fdir.exists(), msg="Project directory should exist after init"
        )
        self.assertTrue(
            (project.fdir / "autoetl.yaml").exists(),
            msg="autoetl.yaml should exist after init",
        )
        self.assertTrue(
            (project.fdir / ".env").exists(),
            msg=".env should exist after init",
        )
        self.assertTrue(
            (project.fdir / "apis").exists(),
            msg="Project directory should exist after init",
        )
        self.assertTrue(
            (project.fdir / "db").exists(),
            msg="Project directory should exist after init",
        )
        self.assertTrue(
            (project.fdir / "etl").exists(),
            msg="Project directory should exist after init",
        )
        self.assertTrue(
            (project.fdir / "fns").exists(),
            msg="Project directory should exist after init",
        )
        self.assertTrue(
            (project.fdir / "serve").exists(),
            msg="Project directory should exist after init",
        )
        self.assertTrue(
            (project.fdir / "domain_knowledge").exists(),
            msg="Project directory should exist after init",
        )
        self.assertTrue(
            (project.fdir / "deployment").exists(),
            msg="Project directory should exist after init",
        )


if __name__ == "__main__":
    t = TestNewProject()
    t.test_init_project()
    # unittest.main()
