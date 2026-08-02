import unittest

from verificar_acervo import render_collection


class CollectionReportTests(unittest.TestCase):
    def test_renders_folders_files_and_nested_subfolders(self):
        nodes = [
            {"id": 1, "type": "dir", "name": "Filmes", "parent": "/", "size": 0, "status": None},
            {"id": 2, "type": "file", "name": "raiz.mkv", "parent": "/Filmes", "size": 1024, "status": "completed"},
            {"id": 3, "type": "dir", "name": "1990S", "parent": "/Filmes", "size": 0, "status": None},
            {"id": 4, "type": "file", "name": "filme.mkv", "parent": "/Filmes/1990S", "size": 2048, "status": "completed"},
        ]

        report = render_collection(nodes)

        self.assertIn(
            "Filmes/\n"
            "    raiz.mkv — 1 KB — completed\n"
            "    1990S/\n"
            "        filme.mkv — 2 KB — completed",
            report,
        )
        self.assertIn("Pastas: 2", report)
        self.assertIn("Arquivos: 2", report)
        self.assertIn("Itens fora da arvore: 0", report)

    def test_reports_nodes_whose_parent_does_not_exist(self):
        report = render_collection([
            {"id": 1, "type": "file", "name": "orfao.mkv", "parent": "/Ausente", "size": 1, "status": None},
        ])
        self.assertIn("ITENS FORA DA ARVORE", report)
        self.assertIn("/Ausente/orfao.mkv", report)
        self.assertIn("Itens fora da arvore: 1", report)


if __name__ == "__main__":
    unittest.main()
