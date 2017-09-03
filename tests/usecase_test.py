"""
Typical use cases.
"""

import sys
import random
import baseLib
import naming_utils
import namingcon.lib as lib


class UseCase(baseLib.BaseCase):

    def test1(self):
        texts = [
            ('sh0110_layoutCameraIsAwesome.0001.exr', 'image_sequence'),
            ('sh0110_lightingRender.0001.exr', 'image_sequence'),
            ('sh0110_lghtingRenderr.0001.exr', 'image_sequence'),
            ('notTheCorrectShot_badSpellling.9999.gif', 'image_sequence'),
            ('shot_name.0001.jpeg', 'image_sequence'),
            ('shot_name.1001.tif', 'image_sequence'),
            ('shot_name.ma', 'maya_scene_file_name'),
            ('shot_name.mb', 'maya_scene_file_name'),
            ('name.ext', 'any_file_name'),
            ('thisFileNameIsValid.abc', 'any_file_name'),
            ('CharacterJohnnyA', 'asset_name_alpha'),
            ('MyEnvironmentA', 'asset_name_alpha'),
            ('Character1', 'asset_name_pad_num'),
            ('Character01', 'asset_name_pad_num'),
            ('Character0001', 'asset_name_pad_num'),
            ('John1', 'asset_name_single_num'),
            ('JOHN', 'asset_name_upper_case'),
            ('JOHHN', 'asset_name_upper_case'),
            ('JOHN1', 'asset_name_upper_case_single_num'),
            ('That gives us back all of our words, though,'
             ' not just the ones that are more than'
             ' 5 letters long.', 'word_sentence'),  # TODO: Work on sentence example.
        ]

        for text, convention in texts:
            print '=' * 80
            print 'text:', text
            print 'convention:', convention
            txt = lib.Text(text, convention)
            print 'best_guess:', repr(txt.best_guess())
            check_map = txt.check_map()
            print 'txt.correct_map:', check_map

            # TODO: How can we tell the user what's wrong? Perhaps we can
            #  produce a "status map", that tells the user for each character
            #  what should go there, if it's wrong.

            for group in txt.split():
                words = group.split()
                for word in words:
                    ok = word.check()
                    if not ok:
                        suggestions = word.suggest()
                        print 'OK:', ok, word._text, suggestions
                    else:
                        print 'OK:', ok, word._text
        return

    def test2(self):
        convention = 'maya_scene_file_name'
        text = 'myShot_layFileName.mb'

        print '=' * 80
        print 'text:', text
        print 'convention:', convention
        txt = lib.Text(text, convention)

        shot_grp = txt.get_group('shot')
        shot_grp.set_text('sh0001')

        name_grp = txt.get_group('name')
        name_grp.set_text('layoutFileName')

        final_text = txt.get_text()
        best_guess = txt.best_guess()
        print 'text:', final_text
        print 'guess:', best_guess
        assert final_text == 'sh0001_layoutFileName.mb'
        assert best_guess == 'sh001_layoutFileName.mb'

    def test3(self):
        convention = 'maya_scene_file_name'
        text = 'myShot_layFileName.mb'

        print '=' * 80
        print 'text:', text
        print 'convention:', convention
        txt = lib.Text(text, convention)
        grps = txt.get_groups()
        for grp in grps:
            if not grp.correct() and grp.get_name() == 'shot':
                print 'shot grp:', grp
                shot = random.choice(naming_utils.get_shot_names())
                grp.set_text(shot)

        final_text = txt.get_text()
        best_guess = txt.best_guess()
        print 'text:', final_text
        print 'guess:', best_guess

    def test4(self):
        conventions = [
            # 'word_names_actor_first', 'word_names_first', 'word_names_last',
            'word_noun', 'word_verb', 'word_adjective',
            'word_any'
        ]
        examples = [
            'cat', 'dog', 'cloud'
            'layout', 'asset', 'light',
            'big', 'huge', 'monstrous', 'gigantic',
            'dynamic', 'green', 'raining',
            'palace', 'ballroom',
            'throwing', 'destroying', 'everlasting'
        ]
        data = {}
        for text in examples:
            for conv in conventions:
                txt = lib.Text(text, conv)

                conv_name = '-'.join(conv.split('_')[1:])
                if text not in data:
                    data[text] = []
                data[text].append({
                    'name': conv_name,
                    'ok': txt.check(),
                    'guess': txt.best_guess()
                })
        for k in sorted(data.keys()):
            print '=' * 80
            print k
            for v in data[k]:
                if v['ok']:
                    print k, v['guess'], v['name']
        assert False
